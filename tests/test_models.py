from auction.models import Auction, Bid
from auction.utils import now


def make_bid(auction, price=1000):
    return Bid.create(
        auction_id=auction.id,
        price=price,
        bids_at=now(),
        confirmed_at=now(),
    )


def test_current_price(testapp, db):
    auction = Auction.create()
    assert auction.current_price == 1000

    make_bid(auction, 1000)
    assert auction.current_price == 1000

    make_bid(auction, 2000)
    assert auction.current_price == 1005

    make_bid(auction, 10000)
    assert auction.current_price == 2005

    make_bid(auction, 20000)
    assert auction.current_price == 10050
