def test_view_auction(testapp, make_auction):
    resp = testapp.get('/auctions/0')
    assert resp.status_code == 404

    auction = make_auction()
    resp = testapp.get('/auctions/{0}'.format(auction.id))
    assert resp.status_code == 200


def test_create_bid(testapp, make_auction):
    auction = make_auction()
    url = '/bids?auction_id={0}'.format(auction.id)

    resp = testapp.get(url)
    assert resp.status_code == 200

    data = {
        'name': 'Name',
        'email': 'test@test.com',
        'price': 1000,
        'consent': True,
    }
    resp = testapp.post(url, data=data)
    assert resp.status_code == 302  # redirection upon validation
