from datetime import datetime
import uuid
from .extensions import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    logo_url = db.Column(db.String(1024))
    plan = db.Column(db.String(50), default='trial')  # 'trial' or 'paid'
    razorpay_customer_id = db.Column(db.String(255))
    razorpay_subscription_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    proposals = db.relationship('Proposal', backref='owner', lazy=True)


class Proposal(db.Model):
    __tablename__ = 'proposals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    client_name = db.Column(db.String(255))
    client_email = db.Column(db.String(255))
    status = db.Column(db.String(50), default='draft')  # draft, sent, accepted
    currency = db.Column(db.String(10), default='INR')
    subtotal = db.Column(db.Numeric(12,2), default=0)
    tax = db.Column(db.Numeric(12,2), default=0)
    total_amount = db.Column(db.Numeric(12,2), default=0)
    notes = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=True)
    share_uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True, default=None)
    share_expiry = db.Column(db.DateTime, nullable=True)
    pdf_url = db.Column(db.String(1024), nullable=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('ProposalItem', backref='proposal', lazy=True, cascade="all, delete-orphan")


class ProposalItem(db.Model):
    __tablename__ = 'proposal_items'
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(12,2), default=0)
    total_price = db.Column(db.Numeric(12,2), default=0)
    position = db.Column(db.Integer, default=0)


class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(255))
    html_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    razorpay_order_id = db.Column(db.String(255))
    razorpay_payment_id = db.Column(db.String(255))
    razorpay_subscription_id = db.Column(db.String(255))
    amount = db.Column(db.Numeric(12,2))
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
