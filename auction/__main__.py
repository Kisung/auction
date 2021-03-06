from datetime import datetime, timedelta
import os

import click

from auction import create_app, log
from auction.models import Auction, db, User
from auction.utils import now


@click.group()
def cli():
    pass


@cli.command()
def create_all():
    with create_app(__name__).app_context():
        db.create_all()


@cli.command()
def drop_all():
    with create_app(__name__).app_context():
        db.drop_all()


@cli.command()
@click.argument('family_name')
@click.argument('given_name')
@click.argument('email')
@click.argument('organization')
def register_user(family_name, given_name, email, organization):
    """Registers a user."""
    with create_app(__name__).app_context():
        user = User.create(
            registered_at=now(),
            family_name=family_name,
            given_name=given_name,
            email=email,
            organization=organization
        )

        log.info('User-{} has been registered.', user.id)


@cli.command()
@click.argument('title')
@click.argument('description')
@click.argument('start_date')
@click.argument('duration', type=int)
def make_auction(title, description, start_date, duration):
    """Makes an auction record.

    :param start_date: yyyy-mm-dd HH:MM:SS UTC
    :param duration: Auction duration in hours
    """
    with create_app(__name__).app_context():
        starts_at = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        auction = Auction.create(
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=duration),
            data={
                # FIXME: This is a temporary workaround
                'payment': os.environ['PAYMENT'],
                # NOTE: We probably need a better name than this...
                'ending_soon_notification_sent': False,
                'sold_notification_sent': False,
            },
        )

        log.info('Auction-{} has been created.', auction.id)


@cli.command()
@click.argument('auction_id')
@click.argument('title')
@click.argument('description')
def update_auction(auction_id, title, description):
    with create_app(__name__).app_context():
        auction = Auction.get(auction_id)
        auction.title = title
        auction.description = description
        db.session.commit()

        log.info('Auction-{} has been updated.', auction.id)


@cli.command()
@click.argument('auction_id')
def send_sold_notification(auction_id):
    """Sends a sold notification given an auction ID."""
    app = create_app(__name__)

    # NOTE: Without SERVER_NAME the url_for() function won't work. This is a
    # temporary workaround and we'll dig into this later.
    app.config['SERVER_NAME'] = ''

    with app.app_context():
        auction = Auction.query.get(auction_id)

        if not auction:
            log.warn('Auction-{} is not found.', auction_id)
            return

        auction.send_sold_notification()


if __name__ == '__main__':
    cli()
