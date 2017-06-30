import os

import pytest

from auction import create_app
from auction.models import db as _db


@pytest.fixture(scope='module')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SERVER_NAME': '',
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


@pytest.fixture(autouse=True)
def testapp(app, db):
    return app.test_client()


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


def teardown(db, record):
    db.session.delete(record)
    db.session.commit()
