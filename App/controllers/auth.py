from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request, current_user
from functools import wraps
from App.models import User, RegularUser, Admin
from .user import create_user
from flask import jsonify

def login(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=user.id)
    return token
  return None

def login_regularUser(username, password):
  user = RegularUser.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=user.id)
    return token
  return None

def login_admin(username, password):
  user = Admin.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=user.id)
    return token
  return None


def signup(username, password):
    user = create_user(username=username, password=password)
    if user:
       return user
    return None

def regularUser_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, RegularUser):
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper


def login_required(required_class):

  def wrapper(f):
    @wraps(f)
    @jwt_required()  # Ensure JWT authentication
    def decorated_function(*args, **kwargs):
      user = User.query.get(get_jwt_identity())
      if user.__class__ != required_class:  # Check class equality
        return jsonify(message='Invalid user role'), 403
      return f(*args, **kwargs)

    return decorated_function

  return wrapper


def setup_jwt(app):
  jwt = JWTManager(app)



  # configure's flask jwt to resolve get_current_identity() to the corresponding user's ID
  @jwt.user_identity_loader
  def user_identity_lookup(user_id):
    return str(user_id)


  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)
  
  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          user_id = get_jwt_identity()
          current_user = User.query.get(user_id)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)