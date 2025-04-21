from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token
from sqlalchemy.exc import IntegrityError
from.index import index_views
from App.database import db

from App.controllers import (
    login, signup, get_user_by_username, login_admin, login_regularUser, get_all_users
)

from App.models import RegularUser, Admin

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    


@auth_views.route('/signup', methods=['GET'])
def signup_page():
  return render_template('signup.html')

@auth_views.route('/', methods=['GET'])
def login_page():
  return render_template('login.html')

@auth_views.route('/signup', methods=['POST'])
def signup_action():
  response = None
  try:
    username = request.form['username']
    password = request.form['password']
    user = signup(username, password)
    response = redirect('/app')
    token = create_access_token(identity=str(user.id))
    set_access_cookies(response, token)
  except IntegrityError:
    db.session.rollback()
    db.session.commit()
    flash('Username already exists')
    response = redirect('/')
  flash('Account created')
  return response

@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
  data = request.form
  token = login(data['username'], data['password'])
  response = None
  user = get_user_by_username(data['username'])
  if token:
    flash('Logged in successfully.')  # send message to next page
    if user.type == "regular":
      response = redirect('/app')
    else :
      response = redirect('/admin')  # redirect to main page if login successful
    set_access_cookies(response, token)
  else:
    flash('Invalid username or password')  # send message to next page
    response = redirect('/')
  return response


@auth_views.route('/logout', methods=['GET'])
@jwt_required()
def logout_action():
  flash('Logged Out')
  response = redirect('/')
  unset_jwt_cookies(response)
  return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response