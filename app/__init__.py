from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.app_context()
    db.init_app(app)

    from .routes.views import views
    from .routes.auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from app.models import User

    create_database(app)

    from app.services.musician_service import add_musicians_to_database
    from app.services.concert_service import add_concerts_to_database

    add_musicians_to_database(app)
    add_concerts_to_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app: Flask) -> None:
    """
    Create a database
    """
    if not database_exists():
        with app.app_context():
            db.create_all()
        print('Created Database!')

def database_exists() -> bool:
    """
    Check if database file exists
    """
    return path.exists('instance/' + DB_NAME)

            

    
