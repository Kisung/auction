from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from auction.forms import BidForm
from auction.models import Auction, Bid


main_module = Blueprint('main', __name__, template_folder='templates')


@main_module.route('/auction/<int:auction_id>')
def view_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    form = BidForm()
    context = {
        'auction': auction,
        'form': form,
    }
    return render_template('view_auction.html', **context)


@main_module.route('/auction/<int:auction_id>/bids')
def view_auction_bids(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    context = {
        'auction': auction,
    }
    return render_template('view_auction_bids.html', **context)


@main_module.route('/bid', methods=['POST'])
def create_bid():
    auction_id = int(request.form['auction_id'])
    auction = Auction.query.get_or_404(auction_id)

    form = BidForm(request.form, auction=auction)
    if not form.validate():
        context = {
            'auction': auction,
            'form': form,
        }
        return render_template('view_auction.html', **context)

    Bid.create(
        auction_id=auction_id,
        name=request.form['name'],
        email=request.form['email'],
        price=parse_price(request.form['price']),
        bids_at=datetime.utcnow(),
        confirmation_code=Bid.generate_confirmation_code(),
    )

    return redirect(url_for('main.view_auction', auction_id=auction.id))


def parse_price(value, currency='KRW'):
    if currency == 'KRW':
        return int(value)
    else:
        raise NotImplementedError
