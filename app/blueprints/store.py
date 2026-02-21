import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Store, Product, Cart, CartItem, Order, OrderItem
from app.dsa.heap import heap_sort_products
from app.dsa.sorting import sort_products_by_price, sort_products_by_name, sort_products_by_newest, quick_sort
from app.dsa.bst import ProductBST
from app.dsa.linked_list import CartLinkedList

store_bp = Blueprint('store', __name__)


def get_or_create_db_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart


def build_cart_linked_list_from_session():
    cart_data = session.get('cart', {})
    ll = CartLinkedList()
    for pid_str, qty in cart_data.items():
        product = Product.query.get(int(pid_str))
        if product and product.is_active:
            ll.append(product.id, qty, product.price, product.name, product.image_url)
    return ll


def build_cart_linked_list_from_db(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    ll = CartLinkedList()
    if cart:
        for item in cart.items:
            product = item.product
            if product and product.is_active:
                ll.append(product.id, item.quantity, product.price, product.name, product.image_url)
    return ll


@store_bp.route('/')
def home():
    stores = Store.query.filter_by(is_active=True).all()
    all_products = Product.query.filter_by(is_active=True).all()
    featured = heap_sort_products(all_products, key='price', reverse=False)[:8]
    return render_template('store/home.html', stores=stores, featured_products=featured)


@store_bp.route('/store/<slug>')
def storefront(slug):
    store = Store.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(store_id=store.id, is_active=True).all()
    sort_param = request.args.get('sort', 'price_asc')
    if sort_param == 'price_asc':
        products = heap_sort_products(products, key='price', reverse=False)
    elif sort_param == 'price_desc':
        products = heap_sort_products(products, key='price', reverse=True)
    elif sort_param == 'name':
        products = sort_products_by_name(products)
    elif sort_param == 'newest':
        products = sort_products_by_newest(products)
    return render_template('store/storefront.html', store=store, products=products, sort_param=sort_param)


@store_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('store/product.html', product=product)


@store_bp.route('/cart')
def cart():
    if current_user.is_authenticated:
        ll = build_cart_linked_list_from_db(current_user.id)
    else:
        ll = build_cart_linked_list_from_session()
    items = ll.to_list()
    total = ll.total()
    return render_template('store/cart.html', cart_items=items, cart_total=total)


@store_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        quantity = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    if quantity < 1:
        quantity = 1

    if current_user.is_authenticated:
        db_cart = get_or_create_db_cart(current_user.id)
        item = CartItem.query.filter_by(cart_id=db_cart.id, product_id=product_id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=db_cart.id, product_id=product_id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        cart_count = sum(i.quantity for i in db_cart.items)
    else:
        cart = session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        session['cart'] = cart
        session.modified = True
        cart_count = sum(cart.values())

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'cart_count': cart_count})
    flash(f'"{product.name}" added to cart!', 'success')
    return redirect(request.referrer or url_for('store.home'))


@store_bp.route('/cart/update', methods=['POST'])
def cart_update():
    data = request.get_json()
    items = data.get('items', [])
    if current_user.is_authenticated:
        db_cart = Cart.query.filter_by(user_id=current_user.id).first()
        if db_cart:
            for entry in items:
                pid = int(entry['id'])
                qty = int(entry['quantity'])
                cart_item = CartItem.query.filter_by(cart_id=db_cart.id, product_id=pid).first()
                if cart_item:
                    if qty <= 0:
                        db.session.delete(cart_item)
                    else:
                        cart_item.quantity = qty
            db.session.commit()
    else:
        cart = session.get('cart', {})
        for entry in items:
            pid = str(entry['id'])
            qty = int(entry['quantity'])
            if qty <= 0:
                cart.pop(pid, None)
            else:
                cart[pid] = qty
        session['cart'] = cart
        session.modified = True
    return jsonify({'success': True})


@store_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    if current_user.is_authenticated:
        db_cart = Cart.query.filter_by(user_id=current_user.id).first()
        if db_cart:
            item = CartItem.query.filter_by(cart_id=db_cart.id, product_id=product_id).first()
            if item:
                db.session.delete(item)
                db.session.commit()
    else:
        cart = session.get('cart', {})
        cart.pop(str(product_id), None)
        session['cart'] = cart
        session.modified = True
    return jsonify({'success': True})


@store_bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    ll = build_cart_linked_list_from_db(current_user.id)
    items = ll.to_list()
    total = ll.total()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('store.cart'))
    return render_template('store/checkout.html', cart_items=items, cart_total=total)


@store_bp.route('/checkout', methods=['POST'])
@login_required
def checkout_post():
    ll = build_cart_linked_list_from_db(current_user.id)
    items = ll.to_list()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('store.cart'))

    # Group items by store
    store_items = {}
    for entry in items:
        product = Product.query.get(entry['product_id'])
        if product:
            sid = product.store_id
            store_items.setdefault(sid, []).append((product, entry['quantity'], entry['price']))

    last_order = None
    for store_id, product_list in store_items.items():
        total = sum(p.price * q for p, q, _ in product_list)
        order = Order(user_id=current_user.id, store_id=store_id, total_amount=total, status='pending')
        db.session.add(order)
        db.session.flush()
        for product, qty, price in product_list:
            oi = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, unit_price=price)
            db.session.add(oi)
        last_order = order

    # Clear DB cart
    db_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if db_cart:
        for item in db_cart.items:
            db.session.delete(item)
    db.session.commit()

    flash('Order placed! Please complete payment.', 'success')
    return redirect(url_for('store.payment_page', order_id=last_order.id))


@store_bp.route('/payment/<int:order_id>')
@login_required
def payment_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('store/checkout_payment.html', order=order, order_items=items)


@store_bp.route('/search')
def search():
    q_raw = request.args.get('q', '').strip()[:100]
    q = re.sub(r'[^\w\s\-]', '', q_raw).lower()  # allow only word chars, spaces, hyphens
    results = []
    if q:
        bst = ProductBST()
        all_products = Product.query.filter_by(is_active=True).all()
        for p in all_products:
            bst.insert(p.name.lower(), p)
        results = bst.search_prefix(q)
        # Deduplicate by id
        seen = set()
        unique_results = []
        for r in results:
            if r.id not in seen:
                seen.add(r.id)
                unique_results.append(r)
        results = quick_sort(unique_results, key=lambda p: p.name.lower())
    return render_template('store/search.html', results=results, query=q)
