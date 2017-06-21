from datetime import datetime
import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auction.forms import BidForm, ConfirmBidForm
from auction.models import Auction, Bid
from auction.utils import now


main_module = Blueprint('main', __name__, template_folder='templates')


@main_module.route('/auctions')
def list_auctions():
    auctions = Auction.query \
        .filter(Auction.ends_at > now()) \
        .order_by(Auction.ends_at)
    context = {
        'auctions': auctions,
    }
    return render_template('list_auctions.html', **context)


@main_module.route('/auction/<int:auction_id>')  # legacy
@main_module.route('/auctions/<int:auction_id>')
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

    previous_winning_bid = bid.auction.winning_bid
    bid.mark_as_confirmed()

    if previous_winning_bid is not None and previous_winning_bid.outbidded:
        previous_winning_bid.send_outbid_notification()

    if bid != bid.auction.winning_bid:
        bid.send_outbid_notification()

    # if bid.outbidded:
    #     flash({
    #         'text': '{}님보다 높은 가격을 제시한 참여자가 있어서 낙찰 '
    #                 '후보에서 밀려났습니다. 더 높은 가격으로 입찰해보세요.'
    #                 ''.format(bid.name),
    #         'image': '<i class="warning sign icon"></i>',
    #     }, 'modal')
    # else:
    flash({
        'text': '{}님의 입찰이 확인되었습니다. 감사합니다.'
                ''.format(bid.name),
        'image': '<i class="thumbs outline up icon"></i>',
    }, 'modal')
    return redirect(url_for('main.view_auction_bids',
                            auction_id=bid.auction.id))


@main_module.route('/outbid-notification/<int:bid_id>')
def view_outbid_notification(bid_id):
    bid = Bid.query.get_or_404(bid_id)
    return render_outbid_notification(bid)


def parse_price(value, currency='KRW'):
    if currency == 'KRW':
        return int(value)
    else:
        raise NotImplementedError


def render_confirmation_email(bid):
    context = {
        'bid': bid,
        'host': os.environ['AUCTION_HOST'],
    }
    return render_template('confirm_bid_email.html', **context)


def render_outbid_notification(bid):
    context = {
        'bid': bid,
        'host': os.environ['AUCTION_HOST'],
    }
    return render_template('outbid_notification.html', **context)
