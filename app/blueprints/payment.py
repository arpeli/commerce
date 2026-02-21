import base64
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Order, Payment

payment_bp = Blueprint('payment', __name__)


def get_mpesa_token():
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    if not consumer_key or not consumer_secret:
        return None
    api_url = current_app.config['MPESA_API_URL']
    credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    response = requests.get(
        f"{api_url}/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {credentials}"}
    )
    if response.status_code == 200:
        return response.json().get('access_token')
    current_app.logger.error("M-Pesa token error %s", response.status_code)
    return None


def stk_push(phone, amount, order_id):
    """Initiate M-Pesa STK push. Returns (success, checkout_request_id, message)."""
    token = get_mpesa_token()
    if not token:
        return False, None, "M-Pesa not configured"

    shortcode = current_app.config['MPESA_SHORTCODE']
    passkey = current_app.config['MPESA_PASSKEY']
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
        "AccountReference": f"Order{order_id}",
        "TransactionDesc": f"Payment for Order {order_id}"
    }

    api_url = current_app.config['MPESA_API_URL']
    response = requests.post(
        f"{api_url}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('ResponseCode') == '0':
            return True, data.get('CheckoutRequestID'), "STK push sent successfully"
    return False, None, "Failed to initiate payment"


@payment_bp.route('/initiate', methods=['POST'])
@login_required
def initiate_payment():
    data = request.get_json()
    order_id = data.get('order_id')
    phone = data.get('phone')

    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    success, checkout_request_id, message = stk_push(phone, order.total_amount, order_id)

    payment = Payment(
        order_id=order_id,
        phone_number=phone,
        amount=order.total_amount,
        mpesa_checkout_request_id=checkout_request_id,
        status='pending' if success else 'failed'
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({'success': success, 'message': message, 'checkout_request_id': checkout_request_id})


@payment_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    if not data:
        return jsonify({'ResultCode': 1, 'ResultDesc': 'No data'}), 400

    stk_callback = data.get('Body', {}).get('stkCallback', {})
    checkout_request_id = stk_callback.get('CheckoutRequestID')
    result_code = stk_callback.get('ResultCode')

    payment = Payment.query.filter_by(mpesa_checkout_request_id=checkout_request_id).first()
    if payment:
        if result_code == 0:
            payment.status = 'completed'
            order = Order.query.get(payment.order_id)
            if order:
                order.status = 'paid'
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        order.mpesa_transaction_id = item.get('Value')
        else:
            payment.status = 'failed'
        db.session.commit()

    return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})


@payment_bp.route('/status/<int:order_id>', methods=['GET'])
@login_required
def payment_status(order_id):
    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    payment = Payment.query.filter_by(order_id=order_id).order_by(Payment.created_at.desc()).first()
    status = payment.status if payment else 'no_payment'
    return jsonify({'success': True, 'status': status, 'order_status': order.status})
