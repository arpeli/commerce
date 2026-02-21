from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from app import db
from app.models import Store, Product, Order, OrderItem
from app.dsa.queue import OrderQueue
from app.dsa.sorting import sort_products_by_name

admin_bp = Blueprint('admin', __name__)


def require_store_owner():
    if not current_user.is_authenticated or not current_user.is_store_owner:
        abort(403)
    store = Store.query.filter_by(owner_id=current_user.id).first()
    if not store:
        flash('You need to create a store first.', 'warning')
        return None, redirect(url_for('auth.create_store'))
    return store, None


@admin_bp.route('/')
@login_required
def dashboard():
    store, redir = require_store_owner()
    if redir:
        return redir
    products = Product.query.filter_by(store_id=store.id, is_active=True).all()
    orders = Order.query.filter_by(store_id=store.id).all()
    revenue = sum(o.total_amount for o in orders if o.status == 'paid')
    pending_queue = OrderQueue()
    for o in orders:
        if o.status == 'pending':
            pending_queue.enqueue(o)
    pending_orders = pending_queue.to_list()
    return render_template('admin/dashboard.html',
                           store=store,
                           product_count=len(products),
                           order_count=len(orders),
                           total_revenue=revenue,
                           pending_orders=pending_orders)


@admin_bp.route('/products')
@login_required
def products():
    store, redir = require_store_owner()
    if redir:
        return redir
    prods = Product.query.filter_by(store_id=store.id).all()
    prods = sort_products_by_name(prods)
    return render_template('admin/products.html', store=store, products=prods)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    store, redir = require_store_owner()
    if redir:
        return redir
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return render_template('admin/add_product.html', store=store, product=None)
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General').strip()
        image_url = request.form.get('image_url', '').strip()
        try:
            price = float(request.form.get('price', 0))
            stock = int(request.form.get('stock', 0))
        except (ValueError, TypeError):
            flash('Invalid price or stock value.', 'error')
            return render_template('admin/add_product.html', store=store, product=None)
        if not name:
            flash('Product name is required.', 'error')
            return render_template('admin/add_product.html', store=store, product=None)
        product = Product(name=name, description=description, price=price,
                          stock=stock, image_url=image_url, category=category,
                          store_id=store.id)
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{name}" added!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', store=store, product=None)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    store, redir = require_store_owner()
    if redir:
        return redir
    product = Product.query.get_or_404(product_id)
    if product.store_id != store.id:
        abort(403)
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            flash('Invalid CSRF token.', 'error')
            return render_template('admin/add_product.html', store=store, product=product)
        product.name = request.form.get('name', product.name).strip()
        product.description = request.form.get('description', product.description).strip()
        product.category = request.form.get('category', product.category).strip()
        product.image_url = request.form.get('image_url', product.image_url).strip()
        try:
            product.price = float(request.form.get('price', product.price))
            product.stock = int(request.form.get('stock', product.stock))
        except (ValueError, TypeError):
            flash('Invalid price or stock value.', 'error')
            return render_template('admin/add_product.html', store=store, product=product)
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', store=store, product=product)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    store, redir = require_store_owner()
    if redir:
        return redir
    product = Product.query.get_or_404(product_id)
    if product.store_id != store.id:
        abort(403)
    product.is_active = False
    db.session.commit()
    flash('Product deactivated.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/orders')
@login_required
def orders():
    store, redir = require_store_owner()
    if redir:
        return redir
    all_orders = Order.query.filter_by(store_id=store.id).order_by(Order.created_at.desc()).all()
    pending_queue = OrderQueue()
    for o in all_orders:
        if o.status == 'pending':
            pending_queue.enqueue(o)
    return render_template('admin/orders.html', store=store, orders=all_orders, pending_queue=pending_queue)
