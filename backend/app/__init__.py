from flask import Flask
from .extensions import db, migrate, login_manager, mail, jwt
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.proposals import proposals_bp
    from .routes.share import share_bp
    from .routes.payments import payments_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(proposals_bp, url_prefix='/api/proposals')
    app.register_blueprint(share_bp, url_prefix='/share')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

    return app
