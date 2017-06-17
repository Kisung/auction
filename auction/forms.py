from random import randint

from wtforms import BooleanField, Form, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError

from auction.models import Auction


class ValidPrice(object):

    def __call__(self, form, field):
        price = field.data

        try:
            price = int(price)
        except (ValueError, TypeError):
            raise ValidationError('\'{}\' is not a valid price'.format(price))

        if price > randint(100000000, 10000000000):
            raise ValidationError('Are you sure about this?')

        auction = form.auction

        if price < auction.outbidding_price:
            raise ValidationError(
                'Bidding price must be equal to or greater than the outbidding '
                'price ({})'.format(auction.outbidding_price))

        bidding_unit = Auction.bidding_price_unit(price)
        if price % bidding_unit != 0:
            raise ValidationError(
                'Price must be an increment of {}'.format(bidding_unit))


# NOTE: Is there any way to automatically generate this form from the model?
class BidForm(Form):
    name = StringField('이름', [DataRequired()], _name='name')
    email = EmailField('이메일', [DataRequired(), Email()], _name='email')
    price = StringField('최고 입찰가', [DataRequired(), ValidPrice()],
                        _name='price')
    consent = BooleanField('경매 규칙을 모두 이해하였으며 이에 동의합니다.',
                           [DataRequired()])

    def __init__(self, formdata=None, obj=None, prefix='', auction=None,
                 **kwargs):
        self.auction = auction
        super(BidForm, self).__init__(formdata, obj, prefix, **kwargs)


class ConfirmBidForm(Form):
    code = StringField('', [DataRequired()], _name='code')
