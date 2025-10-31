from flask import Blueprint, request, jsonify, current_app, abort
import razorpay
from ..extensions import db
from ..models import User, Payment
import hmac, hashlib

payments_bp = Blueprint('payments', __name__)
client = None

def get_rzp_client():
    global client
    if client is None:
        client = razorpay.Client(auth=(current_app.config['RZP_KEY_ID'], current_app.config['RZP_KEY_SECRET']))
    return client

@payments_bp.route('/create_subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get_or_404(user_id)

    rzp = get_rzp_client()
    # Create customer if not exists
    if not user.razorpay_customer_id:
        cust = rzp.customer.create({'name': user.name or user.email, 'email': user.email})
        user.razorpay_customer_id = cust['id']
        db.session.commit()

    # Assumes you have created a plan in Razorpay dashboard or via API; using plan_id
    plan_id = data.get('plan_id')  # e.g. pre-created plan id
    subscription = rzp.subscription.create({
        "plan_id": plan_id,
        "customer_notify": 1,
        "total_count": 12,    # optional - for 12 cycles; remove for indefinite
        "customer_id": user.razorpay_customer_id,
        "trial_end": data.get('trial_end')  # optional
    })
    user.razorpay_subscription_id = subscription['id']
    user.plan = 'paid'
    db.session.commit()

    return jsonify({"subscription_id": subscription['id'], "status": subscription['status']})

@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    signature = request.headers.get('X-Razorpay-Signature')
    secret = current_app.config.get('RZP_WEBHOOK_SECRET')
    # verify signature
    try:
        expected = hmac.new(bytes(secret, 'utf-8'), payload, hashlib.sha256).hexdigest()
        # Razorpay's header is base64 HMAC SHA256; razorpay library has verify_webhook_signature but here is manual
        # Preferred: use razorpay.Utility.verify_webhook_signature
        from razorpay import Utility
        Utility.verify_webhook_signature(payload, signature, secret)
    except Exception as e:
        current_app.logger.error("Webhook signature verification failed: %s", e)
        abort(400)

    event = request.json
    event_type = event.get('event')
    if event_type == 'subscription.charged':
        # handle successful recurring payment
        subscription_id = event['payload']['subscription']['entity']['id']
        # create Payment record, mark user active, etc.
    elif event_type == 'subscription.cancelled':
        # handle cancellation
        subscription_id = event['payload']['subscription']['entity']['id']
        # update user.plan etc.

    # store webhook record optionally
    return jsonify({"status":"ok"}), 200
