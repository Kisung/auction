from datetime import datetime
import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auction.forms import BidForm, ConfirmBidForm
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
        flash({
            'text': '입력하신 이메일 주소로 확인 메시지가 발송되었습니다. '
                    '이메일에 포함된 링크를 클릭하면 입찰이 완료됩니다.',
            'image': '<i class="mail outline icon"></i>',
        }, 'modal')

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
    render = request.args.get('render')
    bid = Bid.query.get_or_404(bid_id)

    if os.environ.get('DEBUG') and request.args.get('render'):
        return render_confirmation_email(bid)

    if code is None:
        form = ConfirmBidForm()
        return render_template('confirm_bid.html', bid=bid, form=form)

    if bid.auction.ended:
        return 'Auction has ended', 400

    if bid.confirmed:
        # FIXME: Is 400 okay?
        return 'Bid already confirmed', 400

    if code != bid.confirmation_code:
        # FIXME: Is 404 okay?
        return 'Invalid confirmation code', 404

    bid.mark_as_confirmed()
    return redirect(url_for('main.view_auction_bids',
                            auction_id=bid.auction.id))


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
            'main.confirm_bid', bid_id=bid.id, code=bid.confirmation_code),
        'link_without_code': os.environ['AUCTION_HOST'] + url_for(
            'main.confirm_bid', bid_id=bid.id),
    }
    return render_template('confirm_bid_email.html', **context)
