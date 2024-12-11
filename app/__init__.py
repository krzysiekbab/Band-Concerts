from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import datetime
import json

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .routes.views import views
    from .routes.auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from app.models import User

    create_database(app)
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
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
    
def add_musicians_to_database(app: Flask) -> None:
    """
    Add forum musicians to database
    """

    from app.services.musician_service import add_musician_to_database

    with app.app_context():
        users_data = load_users_from_file('data/users.json')
        for user_id, user in users_data.items():
            user['id'] = int(user_id)
            add_musician_to_database(user)

def add_concerts_to_database(app: Flask) -> None:
    """
    Add concerts to the database
    """
    
    from app.services.concert_service import add_concert_to_database

    with app.app_context():
        concerts_data = load_users_from_file('data/concerts.json')
        for concert_id, concert in concerts_data.items():
            concert['id'] = int(concert_id)
            add_concert_to_database(concert)

def load_users_from_file(filename: str) -> json:
    with open(filename, 'r') as file:
        users_data = json.load(file)
        
        return users_data
    
def load_concerts_from_file(filename: str) -> json:
    with open(filename, 'r') as file:
        concerts_data = json.load(file)

        return concerts_data


