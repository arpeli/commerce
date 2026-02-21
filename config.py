import os
import warnings

class Config:
    _secret = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    if _secret == 'dev-secret-key-change-in-production':
        warnings.warn(
            "SECRET_KEY is using the default development value. "
            "Set the SECRET_KEY environment variable in production.",
            stacklevel=2,
        )
    SECRET_KEY = _secret
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', '')
    MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://yourdomain.com/payment/callback')
    MPESA_API_URL = 'https://sandbox.safaricom.co.ke'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')
