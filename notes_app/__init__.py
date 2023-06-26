# Flask Imports
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Environment Variables Setup
import os
from dotenv import load_dotenv
load_dotenv()

# Declaring the Constants
SECRET_KEY = os.getenv("SECRET_KEY")
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_URI = os.getenv('POSTGRES_URI')
POSTGRES_DB = os.getenv('POSTGRES_DB')

DB_URI =f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URI}/{POSTGRES_DB}'


# Creating the DB
db = SQLAlchemy()

# Importing the Models
from .models import User,Note

# Importing the Blueprint
from .auth import auth
from .notes import notes


def create_app():

    # Initialising the App and setting its secret key
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY

    # Initialising the Database
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    db.init_app(app)
    create_database(app)


    # Setting Up the Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Registering the Route Blueprints
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

