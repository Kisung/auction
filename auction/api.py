from datetime import datetime

from flask import Blueprint, request, jsonify

from auction.models import Auction, Bid


api_module = Blueprint('api', __name__, template_folder='templates')


@api_module.route('/')
def index():
    pass


@api_module.route('/auction/<int:auction_id>')
def view_auction(auction_id):
    auction = Auction.query.get(auction_id)

    return jsonify(dict(auction))


@api_module.route('/bid', methods=['GET'])
def get_bids():
    auction_id = int(request.args['auction_id'])
    bids = Bid.query.filter(Bid.auction_id == auction_id)

    return jsonify(bids=[dict(x) for x in bids])


@api_module.route('/bid', methods=['POST'])
def make_bid():
    bid = Bid.create(
        auction_id=int(request.json['auction_id']),
        name=request.json['name'],
        email=request.json['email'],
        price=request.json['price'],
        bids_at=datetime.utcnow(),
        confirmation_code=Bid.generate_confirmation_code(),
    )

    return jsonify(dict(bid))


@api_module.route('/bid/<int:bid_id>/confirm', methods=['POST'])
def confirm_bid(bid_id):
    pass
