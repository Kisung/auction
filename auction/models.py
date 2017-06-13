from datetime import datetime
import heapq
from random import randint

import base62
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import uuid64


db = SQLAlchemy()
JsonType = db.String().with_variant(JSON(), 'postgresql')


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
            instance.timestamp = datetime.utcnow()

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
    # starts_at? begins_at?
    begins_at = db.Column(db.DateTime(timezone=False))
    ends_at = db.Column(db.DateTime(timezone=False))

    starting_price = 1000

    bids = db.relationship('Bid', backref='auction', lazy='dynamic')

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

    @property
    def confirmed_bids(self):
        """FIXME: This may have some negative performance impact."""
        return [x for x in self.bids if x.confirmed]

    @property
    def current_price(self):
        prices = [x.price for x in self.confirmed_bids]
        if len(prices) == 0:
            return self.starting_price
        elif len(prices) == 1:
            return prices[0]
        else:
            first, second = heapq.nlargest(2, prices)
            if first == second:
                return first
            else:
                return second + self.bidding_price_unit(second)


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
