import os
import sys

from flask import Flask
from flask_cors import CORS
from logbook import Logger, StreamHandler


__version__ = '0.0.0'
__author__ = 'Sumin Byeon'
__email__ = 'suminb@gmail.com'


StreamHandler(sys.stderr).push_application()
log = Logger('auction')


def create_app(name=__name__, config={},
               static_folder='assets', template_folder='templates'):

    app = Flask(name, static_folder=static_folder,
                template_folder=template_folder)
    app.secret_key = os.environ.get('SECRET', 'secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG'] = bool(os.environ.get('DEBUG', False))

    app.config.update(config)

    # CORS(app, resources={r'*': {'origins': '*'}})

    from auction.models import db
    db.init_app(app)

    from auction.main import main_module
    app.register_blueprint(main_module, url_prefix='')

    from auction.api import api_module
    app.register_blueprint(api_module, url_prefix='/api/v1')

    # @app.route('/')
    # def root():
    #     return app.send_static_file('index.html')

    return app
