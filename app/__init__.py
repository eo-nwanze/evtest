from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from flask_mail import Mail, Message


# Define MEDIA_PATH here
MEDIA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/media')

mail = Mail()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return None  # replace this with your actual User loading logic later

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='templates/static')

    # Set the secret key
    app.secret_key = 'cAliiqj8p1tkoY46QpQbUyZu'  # Replace with a strong, random secret key

    mail.init_app(app)
    # Database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:031089@localhost/file_db'  # Use your own URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import blueprints
    from .views import views
    from .auth import auth
    from .api import api

    # Register blueprints
    app.register_blueprint(views)
    app.register_blueprint(api)
    app.register_blueprint(auth)

    # Configure Flask-Login to redirect to the 'auth.login' view when unauthenticated
    login_manager.login_view = 'auth.login'


    return app

