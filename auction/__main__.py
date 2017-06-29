from datetime import datetime, timedelta

import click

from auction import create_app, log
from auction.models import Auction, db


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


if __name__ == '__main__':
    cli()
