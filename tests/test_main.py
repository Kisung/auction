def test_view_auction(testapp, make_auction):
    resp = testapp.get('/auctions/0')
    assert resp.status_code == 404

    auction = make_auction()
    resp = testapp.get('/auctions/{0}'.format(auction.id))
    assert resp.status_code == 200
