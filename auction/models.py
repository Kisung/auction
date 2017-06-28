from datetime import datetime
import heapq
from random import randint

import base62
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
import requests
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.attributes import flag_modified
import uuid64

from auction import cache
from auction.utils import now, send_email


db = SQLAlchemy()
JSONType = db.String().with_variant(JSON(), 'postgresql')


class CRUDMixin(object):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False,
                   default=uuid64.issue())

    @classmethod
    def create(cls, commit=True, **kwargs):
        if 'id' not in kwargs:
            kwargs.update(dict(id=uuid64.issue()))
        instance = cls(**kwargs)

        if hasattr(instance, 'timestamp') \
                and getattr(instance, 'timestamp') is None:
            instance.timestamp = now()

        return instance.save(commit=commit)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    # We will also proxy Flask-SqlAlchemy's get_or_404
    # for symmetry
    @classmethod
    def get_or_404(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def exists(cls, **kwargs):
        row = cls.query.filter_by(**kwargs).first()
        return row is not None

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def __iter__(self):
        for column in self.__table__.columns:
            attr = getattr(self, column.name)
            yield column.name, str(attr) if attr is not None else None


class Auction(CRUDMixin, db.Model):

    title = db.Column(db.String)
    description = db.Column(db.Text)
    starts_at = db.Column(db.DateTime(timezone=False))
    ends_at = db.Column(db.DateTime(timezone=False))

    starting_price = 1000

    bids = db.relationship('Bid', backref='auction', lazy='dynamic')

    data = db.Column(JSONType)

    @classmethod
    def bidding_price_unit(cls, price):
        """Determines an increment of a bidding price given a price.

        See more details: https://www.miraeassetdaewoo.com/hki/hki3061/n65.do
        """
        if price < 1000:
            return 1
        elif price < 5000:
            return 5
        elif price < 10000:
            return 10
        elif price < 50000:
            return 50
        elif price < 100000:
            return 100
        elif price < 500000:
            return 500
        else:
            return 1000

    def has_bidding(self, confirmed_only=True):
        if confirmed_only:
            return self.confirmed_bids.count() > 0
        else:
            return self.bids.count() > 0

    @property
    def ordered_bids(self):
        return self.bids.order_by(Bid.price.desc(), Bid.bids_at)

    @property
    def confirmed_bids(self):
        return self.ordered_bids.filter(Bid.confirmed_at != None)  # noqa

    @property
    def current_price(self):
        """Calculates the current price."""
        prices = [x.price for x in self.confirmed_bids]
        if len(prices) <= 1:
            return self.starting_price
        else:
            first, second = heapq.nlargest(2, prices)
            if first == second:
                return first
            else:
                return second + self.bidding_price_unit(second)

    @property
    def outbidding_price(self, current_price=None):
        """Calculates the minimum price that outbids the current price."""
        if current_price is None:
            current_price = self.current_price

        if self.confirmed_bids.count() == 0:
            return self.starting_price
        else:
            return current_price + self.bidding_price_unit(current_price)

    @property
    @cache.cached(timeout=300, key_prefix='gdocs/%s')
    def gdocs_description(self):
        """Fetches HTML from a published Google Docs document.

        TODO: Think of a better name.
        TODO: Set up some kind of cache.
        """
        if not self.description.startswith('https://docs.google.com') \
                and not self.description.startswith('gdocs://'):
            raise ValueError('Not a valid Google Docs URL')

        url = 'https' + self.description[len('gdocs'):]

        resp = requests.get(url)
        soup = BeautifulSoup(resp.content)
        content = soup.find(id='contents')
        # TODO: Select div#contents' child nodes

        return content

    @property
    def started(self):
        return now() >= self.starts_at

    @property
    def ended(self):
        """Indicates whether the auction has been ended."""
        return now() >= self.ends_at

    @property
    def starts_in(self):
        return self.starts_at - now()

    @property
    def remaining(self):
        return self.ends_at - now()

    @property
    def winning_bid(self):
        """A winning bid. Note that this returns a value rather than a query.
        """
        return self.confirmed_bids.limit(1).first()

    def notify_outbidded_participants(self, except_=None):
        for bid in self.confirmed_bids:
            if except_ is not None and bid == except_:
                continue

            if bid.outbidded:
                bid

    def send_sold_notification(self):
        if not self.data.get('payment'):
            raise ValueError('Payment information is required')

        if self.data.get('sold_notification_sent', False):
            raise ValueError(
                'Auction-{0} already has been notified'.format(self.id))

        from auction.main import render_sold_notification
        html = render_sold_notification(self)

        try:
            resp = send_email([self.winning_bid.email],
                              '[천원경매] 낙찰', html)
        except:
            # FIXME: Does send_mail even raise an exception?
            # FIXME: Handle the exception
            pass
        else:
            self.data['sold_notification_sent'] = True

            # Without this, the JSON field won't get updated.
            # Refer https://bashelton.com/2014/03/updating-postgresql-json-fields-via-sqlalchemy/  # noqa
            # for more details.
            flag_modified(self, 'data')

            self.save()

            return resp


class Bid(CRUDMixin, db.Model):

    auction_id = db.Column(db.BigInteger, db.ForeignKey('auction.id'))

    #: Bidder's full name
    name = db.Column(db.String)

    #: Bidder's email address
    email = db.Column(db.String)

    #: Maximum bidding price
    price = db.Column(db.Integer)

    #: This will be used to determine earlier bids in case of a conflict
    bids_at = db.Column(db.DateTime(timezone=False))

    confirmation_code = db.Column(db.String)

    #: If None, it indicates an unconfirmed bid
    confirmed_at = db.Column(db.DateTime(timezone=False), nullable=True)

    @classmethod
    def generate_confirmation_code(cls):
        """Generates a random code."""
        code = randint(0x100000000000, 0xffffffffffff)
        return base62.encode(code)

    @property
    def confirmed(self):
        """Indicates whether the bid has been confirmed."""
        return self.confirmed_at is not None

    @property
    def outbidded(self):
        """Indicates whether the bid has been outbidded."""
        return self.price < self.auction.current_price \
            or (self.price == self.auction.current_price
                and self != self.auction.winning_bid)

    @property
    def censored_email(self):
        username, domain = self.email.split('@')
        return '{}...{}@{}'.format(username[:2], username[-1], domain)

    @property
    def disclosed_price(self):
        """Returns a publicly disclosed price."""
        current_price = self.auction.current_price
        if self.price > current_price:
            return current_price
        else:
            return self.price

    def mark_as_confirmed(self):
        self.confirmed_at = datetime.utcnow()
        db.session.commit()

    # FIXME: send_ functions should be somewhere else
    # (i.e., under the controller)

    def send_confirmation_email(self):
        from auction.main import render_confirmation_email
        html = render_confirmation_email(self)

        return send_email([self.email], '[천원경매] 입찰 확인', html)

    def send_outbid_notification(self):
        from auction.main import render_outbid_notification
        html = render_outbid_notification(self)

        return send_email([self.email], '[천원경매] Outbid Notification', html)
