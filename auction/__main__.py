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
def make_auction(title, description):
    with create_app(__name__).app_context():
        now = datetime.utcnow()
        auction = Auction.create(
            title=title,
            description=description,
            starts_at=now,
            ends_at=now + timedelta(minutes=30),
        )

        log.info('Auction-{} has been created.', auction.id)


if __name__ == '__main__':
    cli()
