from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Declaring the Constants
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'password'
POSTGRES_URI = '127.0.0.1:5432'
POSTGRES_DB = "notes_app"

DB_URI =f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URI}/{POSTGRES_DB}'


# Creating the DB
db = SQLAlchemy()

# Importing the Models
from .models import User,Note

# Importing the Blueprint
from .auth import auth
from .notes import notes


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = "helloworld"

    # Initialising the Database
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    db.init_app(app)
    create_database(app)


    # Setting Up the Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    app.register_blueprint(auth,url_prefix="/")
    app.register_blueprint(notes,url_prefix="/notes")


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return app

def create_database(app):
    with app.app_context():
        db.create_all()
        print("Created Database!")

