from flask import Blueprint, render_template

from auction.models import Auction, Bid


main_module = Blueprint('main', __name__, template_folder='templates')


@main_module.route('/auction/<int:auction_id>')
def view_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    context = {
        'auction': auction,
    }
    return render_template('view_auction.html', **context)
