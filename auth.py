from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm
from storage import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow().isoformat()
        user.save()

        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.get_by_username(form.username.data):
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.register'))

        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        user.save()

        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def init_auth(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    app.register_blueprint(auth_bp)