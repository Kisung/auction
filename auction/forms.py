from wtforms import Form, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, ValidationError


class ValidPrice(object):
    def __init__(self, message=None):
        pass

    def __call__(self, form, field):
        price = field.data

        try:
            price = int(price)
        except (ValueError, TypeError):
            raise ValidationError('\'{}\' is not a valid price'.format(price))

        if price % 100 != 0:
            raise ValidationError('Price must be divisible by 100')


# NOTE: Is there any way to automatically generate this form from the model?
class BidForm(Form):
    name = StringField('이름', [DataRequired()], _name='name')
    email = EmailField('이메일', [DataRequired(), Email()], _name='email')
    price = StringField('최고 입찰가', [DataRequired(), ValidPrice()],
                        _name='price')
