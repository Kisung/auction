from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from auction import login_manager
from auction.forms import LoginForm
from auction.models import User


user_module = Blueprint('user', __name__, template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get_or_404(user_id)
    return user


@user_module.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        # FIXME: Check for password
        login_user(user)

        # TODO: Check if safe to redirect
        url = request.args.get('url')
        return redirect(url or url_for('main.list_auctions'))

    return render_template('login.html', form=form)


@user_module.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.list_auctions'))
