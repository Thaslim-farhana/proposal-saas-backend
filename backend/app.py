from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_mail import Mail, Message
from flask_cors import CORS
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
mail = Mail(app)

# ---------------------------------------------------
# Database Model Example
# ---------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# ---------------------------------------------------
# Routes
# ---------------------------------------------------
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Flask SaaS App!"})

# Signup route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.username)
        return jsonify({"access_token": access_token})
    return jsonify({"message": "Invalid credentials"}), 401

# Protected route
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    return jsonify({"message": "Access granted to protected route!"})

# Test email route
@app.route('/send-mail')
def send_mail():
    msg = Message("Test Email", sender=app.config['MAIL_USERNAME'], recipients=["youremail@example.com"])
    msg.body = "This is a test email from Flask app."
    mail.send(msg)
    return jsonify({"message": "Email sent successfully!"})

# ---------------------------------------------------
# Run Flask App
# ---------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
