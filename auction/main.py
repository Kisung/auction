import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auction.forms import BidForm, ConfirmBidForm
from auction.models import Auction, Bid, User
from auction.utils import now


main_module = Blueprint('main', __name__, template_folder='templates')


@main_module.route('/')
def index():
    return redirect(url_for('main.list_auctions'))


@main_module.route('/auctions')
def list_auctions():
    auctions = Auction.query \
        .order_by(Auction.ends_at.desc())
    context = {
        'auctions': auctions,
    }
    return render_template('list_auctions.html', **context)


@main_module.route('/auctions/<int:auction_id>')
def view_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    form = BidForm()
    context = {
        'auction': auction,
        'form': form,
    }
    return render_template('view_auction.html', **context)


@main_module.route('/auctions/<int:auction_id>/bids')
def view_auction_bids(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    context = {
        'auction': auction,
    }
    return render_template('view_auction_bids.html', **context)


@main_module.route('/bids', methods=['GET', 'POST'])
def create_bid():
    auction_id = int(request.args['auction_id'])
    auction = Auction.query.get_or_404(auction_id)

    form = BidForm(request.form, auction, auction=auction)
    if request.method == 'POST' and form.validate():
        if not auction.started:
            # TODO: Show this message with a template
            return 'The auction has not started yet', 403

        if auction.ended:
            # TODO: Show this message with a template
            return 'The auction has ended', 403

        bid = Bid.create(
            auction_id=auction_id,
            name=form.name.data,
            email=form.email.data,
            price=parse_price(form.price.data),
            bids_at=now(),
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


@main_module.route('/bids/<int:bid_id>/confirm')
def confirm_bid(bid_id):
    code = request.args.get('code')
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


@main_module.route('/sellers/<int:seller_id>')
def view_seller(seller_id):
    seller = User.query.get_or_404(seller_id)
    context = {
        'seller': seller,
    }
    return render_template('view_seller.html', **context)


@main_module.route('/bids/<int:bid_id>/outbidded')
def view_outbid_notification(bid_id):
    if not os.environ.get('DEBUG', False):
        return '', 403

    bid = Bid.query.get_or_404(bid_id)
    return render_outbid_notification(bid)


@main_module.route('/auctions/<int:auction_id>/sold')
def view_sold_notification(auction_id):
    if not os.environ.get('DEBUG', False):
        return '', 403

    auction = Auction.query.get_or_404(auction_id)
    return render_sold_notification(auction)


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


def render_sold_notification(auction):
    context = {
        'auction': auction,
    }
    return render_template('sold_notification.html', **context)
