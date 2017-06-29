from auction.models import Auction, Bid
from auction.utils import now


def make_bid(auction, price=1000, confirmed=True):
    return Bid.create(
        auction_id=auction.id,
        price=price,
        bids_at=now(),
        confirmed_at=now() if confirmed else None,
    )


def test_has_bidding():
    auction = Auction.create()

    # Initially has no bidding
    assert not auction.has_bidding(confirmed_only=True)
    assert not auction.has_bidding(confirmed_only=False)

    make_bid(auction, 1000, confirmed=False)

    # Unconfirmed bid has no effect on the confirmed bids count
    assert not auction.has_bidding(confirmed_only=True)
    assert auction.has_bidding(confirmed_only=False)

    make_bid(auction, 1500)

    # Auction now has one confirmed bidding, total of two biddings
    assert auction.has_bidding(confirmed_only=True)
    assert auction.has_bidding(confirmed_only=False)


def test_current_price():
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


def test_disclosed_price():
    auction = Auction.create()

    bid1 = make_bid(auction, 1000)
    assert bid1.disclosed_price == 1000

    bid2 = make_bid(auction, 2000)
    assert bid1.disclosed_price == 1000
    assert bid2.disclosed_price == 1005

    bid3 = make_bid(auction, 3000, False)
    assert bid1.disclosed_price == 1000
    assert bid2.disclosed_price == 1005
    assert bid3.disclosed_price == 1005
