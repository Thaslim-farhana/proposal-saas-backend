from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, login_manager
from ..models import User
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg":"Email already registered"}), 400

    user = User(email=email, password_hash=generate_password_hash(password), name=name)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"registered"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"msg":"Invalid credentials"}), 401
    login_user(user)
    return jsonify({"msg":"logged_in", "user_id": user.id})
