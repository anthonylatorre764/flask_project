from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate





login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()


# app factory
def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # register packages
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # login_manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'You must be logged in to view this page!'
    login_manager.login_message_category = 'warning'

    # Importing Blueprint
    from app.blueprints.main import main
    from app.blueprints.auth import auth
    

    # Register Blueprint
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    return app


# from app import routes, models