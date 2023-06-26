from flask import Blueprint,request,jsonify
from flask_login import login_user,logout_user,login_required,current_user

# Hashing Utilities
from werkzeug.security import generate_password_hash,check_password_hash


# Importing the Database Models and Instance
from .models import User
from . import db

# Creating the Blueprint Instance
auth = Blueprint("auth",__name__)


# Delete all Users
@auth.route('/del')
def del_users():
    User.query.delete()
    db.session.commit()
    return "Done"


# Sign Up Route
@auth.route('/sign-up',methods=['POST'])
def signup():
    # Getting the Credentials
    jsonified_req = request.json

    email = jsonified_req["email"]
    username = jsonified_req["username"]
    password = jsonified_req["password"]
    password_confirm = jsonified_req["password_confirm"]

    # Checking whether the User already exists or not
    user_with_same_email = User.query.filter_by(email=email).first()
    user_with_same_username = User.query.filter_by(username=username).first()

    if user_with_same_email:
        return jsonify({"status" : "error", "msg" : "Email already Exists! Kindly Login using the necessary credentials"})
    elif user_with_same_username:
        return jsonify({"status" : "error", "msg" : "Username already Exists!"})
    elif password != password_confirm:
        return jsonify({"status" : "error", "msg" : "Passwords do not match!"})
    else:
        new_user = User(email=email,username=username,password=generate_password_hash(password,method="sha256"))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user,remember=True)
        return jsonify({"status": "success","msg":"User Created and Logged In!","user_id":new_user.id})


# Login Route
@auth.route('/login',methods = ['GET','POST'])
def login():

    if request.method == 'GET':
        return jsonify({"status" : "Unauthorised", "msg" : "Please Login to Access the Feature!"})
    
 # Getting the Credentials
    jsonified_req = request.json

    email = jsonified_req["email"]
    password = jsonified_req["password"]

    user = User.query.filter_by(email=email).first()

    '''
    Case - 1: User with that email Does not exist
    Case - 2: User with that email exists but password does not match
    Case - 3: User with that email exists and password matches
    '''

    # Case - 1
    if not user:
        return jsonify({"status": "error" , "msg" : "User Does not Exist!"})
    else:
        # Case - 2
        if(check_password_hash(user.password,password)):
            login_user(user,remember=True)
            return jsonify({"status" : "success", "msg" : "User Logged In", "user_id" : user.id})
        
        # Case - 3
        else:
            return jsonify({"status": "error", "msg" : "Credentials Not Matched!"})

@auth.route('/logout',methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "Current User Logged Out!"})
