from datetime import datetime
import os

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


@main_module.route('/bid', methods=['GET', 'POST'])
def create_bid():
    auction_id = int(request.args['auction_id'])
    auction = Auction.query.get_or_404(auction_id)

    form = BidForm(request.form, auction, auction=auction)
    if request.method == 'POST' and form.validate():
        if auction.ended:
            # TODO: Show this message with a template
            return 'The auction has ended', 403

        bid = Bid.create(
            auction_id=auction_id,
            name=request.form['name'],
            email=request.form['email'],
            price=parse_price(request.form['price']),
            bids_at=datetime.utcnow(),
            confirmation_code=Bid.generate_confirmation_code(),
        )
        bid.send_confirmation_email()
        return redirect(
            url_for('main.view_auction_bids', auction_id=auction.id))

    context = {
        'auction': auction,
        'form': form,
    }
    return render_template('create_bid.html', **context)


@main_module.route('/bid/<int:bid_id>/confirm')
def confirm_bid(bid_id):
    code = request.args.get('code')
    bid = Bid.query.get_or_404(bid_id)

    # FIXME: Maybe we should flatten the following if-else statements
    if code:
        if code == bid.confirmation_code:
            if bid.confirmed:
                # FIXME: Is 400 okay?
                return 'Bid already confirmed', 400
            else:
                bid.mark_as_confirmed()
                return redirect(url_for('main.view_auction_bids',
                                        auction_id=bid.auction.id))
        else:
            # FIXME: Is 404 okay?
            return 'Invalid confirmation code', 404
    else:
        # TODO: Show a page to manually enter the code
        return render_confirmation_email(bid)


def parse_price(value, currency='KRW'):
    if currency == 'KRW':
        return int(value)
    else:
        raise NotImplementedError


def render_confirmation_email(bid):
    context = {
        'bid': bid,
        'host': os.environ['AUCTION_HOST'],
        'link': os.environ['AUCTION_HOST'] + url_for(
            'main.confirm_bid', bid_id=bid.id, code=bid.confirmation_code)
    }
    return render_template('bidding_confirmation.html', **context)
