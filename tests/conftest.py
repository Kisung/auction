import os

import pytest

from auction import create_app
from auction.models import db as _db


@pytest.fixture(scope='module')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
    }
    settings_override['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app = create_app(__name__, config=settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def testapp(app, db):
    return app.test_client()


@pytest.fixture(scope='module')
def db(app, request):
    """Session-wide test database."""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


def teardown(db, record):
    db.session.delete(record)
    db.session.commit()
