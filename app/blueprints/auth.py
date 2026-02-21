import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from app import db
from app.models import User, Store

auth_bp = Blueprint('auth', __name__)


def generate_slug(name):
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug).strip('-')
    return slug


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('store.home'))
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return render_template('auth/login.html')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('store.home'))
        flash('Invalid email or password.', 'error')
    return render_template('auth/login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('store.home'))
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return render_template('auth/signup.html')
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        is_store_owner = request.form.get('is_store_owner') == 'on'

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/signup.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('auth/signup.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/signup.html')

        user = User(name=name, email=email, is_store_owner=is_store_owner)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully!', 'success')
        if is_store_owner:
            return redirect(url_for('auth.create_store'))
        return redirect(url_for('store.home'))
    return render_template('auth/signup.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('store.home'))


@auth_bp.route('/create-store', methods=['GET', 'POST'])
@login_required
def create_store():
    if not current_user.is_store_owner:
        flash('You must be a store owner to create a store.', 'error')
        return redirect(url_for('store.home'))
    existing = Store.query.filter_by(owner_id=current_user.id).first()
    if existing:
        flash('You already have a store.', 'info')
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return render_template('auth/create_store.html')
        store_name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not store_name:
            flash('Store name is required.', 'error')
            return render_template('auth/create_store.html')
        base_slug = generate_slug(store_name)
        slug = base_slug
        counter = 1
        while Store.query.filter_by(slug=slug).first():
            slug = f'{base_slug}-{counter}'
            counter += 1
        store = Store(name=store_name, slug=slug, description=description, owner_id=current_user.id)
        db.session.add(store)
        db.session.commit()
        flash(f'Store "{store_name}" created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('auth/create_store.html')
