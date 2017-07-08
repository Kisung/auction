from datetime import datetime
import re
from random import randint

from flask_wtf import Form
from wtforms import BooleanField, Form, SelectField, StringField
from wtforms.fields.html5 import DateTimeField, EmailField
from wtforms.validators import DataRequired, Email, ValidationError

from auction.models import Auction


# TODO: Move these validators somewhere else

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
                'Bidding price must be equal to or greater than the '
                'outbidding price ({})'.format(auction.outbidding_price))

        bidding_unit = Auction.bidding_price_unit(price)
        if price % bidding_unit != 0:
            raise ValidationError(
                'Price must be an increment of {}'.format(bidding_unit))


class ValidGDocsURL(object):

    pattern = r'https://docs.google.com/document/d/[0-9A-Za-z_-]+/pub'

    def __call__(self, form, field):
        if not re.match(self.pattern, field.data):
            raise ValidationError(
                '{0} is not a valid Google Docs URL'.format(field.data))


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


class CreateAuctionForm(Form):
    title = StringField('상품명', [DataRequired()], _name='title')
    description = StringField(
        '상품 설명 (Google Docs)', [DataRequired(), ValidGDocsURL()],
        _name='description')
    starts_at = DateTimeField(
        '시작일', [DataRequired()], _name='starts_at',
        default=datetime.utcnow())
    duration = SelectField(
        '경매 기간', [DataRequired()],
        coerce=int,
        choices=[
            (4, '4시간'), (8, '8시간'),
            (24, '1일'), (48, '2일'), (72, '3일')],
        default=24,
    )

class LoginForm(Form):
    email = EmailField('이메일', [DataRequired()], _name='email')
    password = PasswordField('비밀번호', [DataRequired()], _name='password')
