from datetime import timedelta
import os

import pytest

from auction import create_app
from auction.models import Auction, Bid, db as _db, User
from auction.utils import now


@pytest.fixture(scope='module')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SERVER_NAME': 'localhost',
    }
    settings_override['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DB_URL']
    app = create_app(__name__, config=settings_override)

    # # Establish an application context before running the tests.
    # ctx = app.app_context()
    # ctx.push()

    # def teardown():
    #     ctx.pop()

    # request.addfinalizer(teardown)
    # return app

    return app


@pytest.fixture
def testapp(app, db):
    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope='module', autouse=True)
def db(app, request):
    """Session-wide test database."""
    def teardown():
        # Not sure about this...
        with app.app_context():
            _db.drop_all()

    request.addfinalizer(teardown)

    _db.app = app
    with app.app_context():
        _db.create_all()

        yield _db


@pytest.fixture
def make_auction(make_user):
    def make(seller=None):
        if seller is None:
            seller = make_user()

        starts_at = now()
        return Auction.create(
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=24),
            seller_id=seller.id,
            description='https://docs.google.com/document/d/_/pub'
        )
    return make


@pytest.fixture
def make_bid():
    def make(auction, price=1000, confirmed=True):
        return Bid.create(
            auction_id=auction.id,
            price=price,
            bids_at=now(),
            confirmed_at=now() if confirmed else None,
        )
    return make


@pytest.fixture
def make_user():
    def make():
        return User.create(
            email='jason.bourne@cia.giv',
            family_name='Bourne',
            given_name='Jason',
        )
    return make


def teardown(db, record):
    db.session.delete(record)
    db.session.commit()
