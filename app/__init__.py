import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    from app.blueprints.auth import auth_bp
    from app.blueprints.store import store_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.payment import payment_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(store_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(payment_bp, url_prefix='/payment')

    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_cart_count():
        count = 0
        try:
            if current_user.is_authenticated:
                from app.models import Cart, CartItem
                cart = Cart.query.filter_by(user_id=current_user.id).first()
                if cart:
                    count = sum(item.quantity for item in cart.items)
            else:
                cart = session.get('cart', {})
                count = sum(cart.values())
        except (AttributeError, TypeError):
            count = 0
        return {'cart_count': count}

    return app
