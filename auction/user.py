from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from auction import login_manager
from auction.forms import LoginForm
from auction.models import User
from auction.oauth import OAuthSignIn
from auction.utils import now


user_module = Blueprint('user', __name__, template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get_or_404(user_id)
    return user


@user_module.route('/login', methods=['GET', 'POST'])
def login():
    """This method is depreciated. We will no longer support in-house user
    authentication.
    """
    form = LoginForm(request.form)
    context = {'form': form, 'errors': []}
    if form.validate_on_submit():
        context['errors'].append('Invalid email or password')

    return render_template('login.html', **context)


@user_module.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.list_auctions'))


@user_module.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@user_module.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User.create(
            registered_at=now(),
            social_id=social_id,
            email=email,
        )
    login_user(user, True)
    return redirect(url_for('main.index'))
