"""Authentication routes"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import RegistrationForm, LoginForm
from app.models import User
from app.extensions import db


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            name=form.name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/auth.html', form=form, mode='register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('tournaments.list'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/auth.html', form=form, mode='login')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/account')
@login_required
def account():
    """User account page"""
    songs = current_user.songs.all()
    return render_template('auth/auth.html', user=current_user, songs=songs, mode='account')
