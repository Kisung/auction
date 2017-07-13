from functools import partial
import os
import sys

from babel.numbers import format_currency
from flask import Flask
from flask_cache import Cache
from flask_login import LoginManager
from logbook import Logger, StreamHandler


__version__ = '0.0.0'
__author__ = 'Sumin Byeon'
__email__ = 'suminb@gmail.com'


StreamHandler(sys.stderr).push_application()
log = Logger('auction')

cache = Cache()
login_manager = LoginManager()


def create_app(name=__name__, config={},
               static_folder='assets', template_folder='templates'):

    app = Flask(name, static_folder=static_folder,
                template_folder=template_folder)
    app.secret_key = os.environ.get('SECRET', 'secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG'] = bool(os.environ.get('DEBUG', False))

    app.config['OAUTH_CREDENTIALS'] = {
        'google': {
            'id': os.environ['GOOGLE_OAUTH_ID'],
            'secret': os.environ['GOOGLE_OAUTH_SECRET'],
        },
        'facebook': {
            'id': '',
            'secret': '',
        },
        'twitter': {
            'id': '',
            'secret': '',
        },
    }

    app.config.update(config)

    cache.init_app(app, config={
        'CACHE_TYPE': 'simple',
    })

    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    from auction.models import db
    db.init_app(app)

    from auction.main import main_module
    app.register_blueprint(main_module, url_prefix='')

    from auction.user import user_module
    app.register_blueprint(user_module, url_prefix='/users')

    from auction.api import api_module
    app.register_blueprint(api_module, url_prefix='/api/v1')

    app.jinja_env.filters['format_currency'] \
        = partial(format_currency, currency='KRW')

    from auction.utils import format_datetime, human_readable
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['human_readable'] = human_readable

    return app
