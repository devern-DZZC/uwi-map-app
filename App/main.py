import os, csv, re
from flask import Flask, redirect, render_template, jsonify, request, send_from_directory, flash, url_for
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, IntegrityError
from App.models import db, User, Location, UserLocation, Admin, RegularUser
from datetime import timedelta
from functools import wraps

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
    current_user,
)


def create_app():
  app = Flask(__name__, static_url_path='/static')
  CORS(app)
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
      app.root_path, 'data.db')
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
  app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
  app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
  app.config["JWT_COOKIE_SECURE"] = True
  app.config["JWT_SECRET_KEY"] = "super-secret"
  app.config["JWT_COOKIE_CSRF_PROTECT"] = False
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

  app.app_context().push()
  return app


app = create_app()
db.init_app(app)

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
  return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
  flash("Your session has expired. Please log in again.")
  return redirect(url_for('login'))


def create_users():
  rob = RegularUser(username="rob", password="robpass")
  bob = RegularUser(username="bob", password="bobpass")
  sally = RegularUser(username="sally", password="sallypass")
  pam = Admin(staff_id='1000',username="pam", password="pampass")
  db.session.add_all([rob, bob, sally, pam])
  db.session.commit()

def parse_locations():
    with open('locations.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        locations = []
        
        for row in csv_reader:
            name = row[0]  
            c = row[1]     
            building_type = row[2]

            coords = c.split(', ')
            lat, lon = float(coords[0]), float(coords[1])
            
            if lon is not None and lat is not None:
                print(f"Location: {name}, Description: {building_type}, Coordinates: ({lat}, {lon})")
                location = Location(name=name, latitude=lat, longitude=lon, description=building_type)
                locations.append(location)

        db.session.add_all(locations)
        db.session.commit()

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

def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=user)
    return token
  return None


def initialize_db():
  db.drop_all()
  db.create_all()
  parse_locations()
  create_users()
  print('database intialized')



@app.route('/')
def login():
  return render_template('login.html')

@app.route("/app", methods=['GET'])
@app.route("/app/<int:location_id>", methods=['GET'])
@jwt_required()
def home(location_id=None):
    if location_id:
      location = Location.query.get_or_404(location_id)
      location_name = location.name
    else:
       location = Location.query.get(1)
       location_name = ""
    return render_template(
        "index.html",
        current_location=location,
        current_user=current_user,
        locations=UserLocation.query.filter_by(user_id=current_user.id).all(),
        location_id=location_id,
        location_name = location_name
    )


@app.route('/signup', methods=['GET'])
def signup():
  return render_template('signup.html')

@app.route('/admin')
@login_required(Admin)
def admin():
  return render_template('admin.html')


@app.route('/signup', methods=['POST'])
def signup_action():
  data = request.form  # get data from form submission
  newuser = RegularUser(username=data['username'], password=data['password'])  # create user object
  response = None
  try:
    db.session.add(newuser)
    db.session.commit()  # save user
    token = login_user(data['username'], data['password'])
    response = redirect(url_for('home'))
    set_access_cookies(response, token)
    flash('Account Created!')  
  except Exception:  
    db.session.rollback()
    flash("username or email already exists")  
    response = redirect(url_for('login'))
  return response


@app.route('/login', methods=['POST'])
def login_action():
  data = request.form
  token = login_user(data['username'], data['password'])
  response = None
  user = User.query.filter_by(username=data['username']).first()
  if token:
    flash('Logged in successfully.')  # send message to next page
    if user.type == "regular user":
      response = redirect(url_for('home'))
    else :
      response = redirect(url_for('admin'))  # redirect to main page if login successful
    set_access_cookies(response, token)
  else:
    flash('Invalid username or password')  # send message to next page
    response = redirect(url_for('login'))
  return response


@app.route('/add_location', methods=['POST'])
@login_required(Admin)
def add_location():
    data = request.get_json()
    name = data['name']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    building_type = data['building_type'] 

    new_location = Location(name=name, description=building_type, latitude=latitude, longitude=longitude)
    db.session.add(new_location)
    db.session.commit()
    if request.is_json:
        return jsonify(success=True)
    else:
        return redirect("/")
    
@app.route('/save_location/<int:location_id>', methods=['POST'])
@login_required(RegularUser)
def save_location(location_id):
    data = request.form
    if not data:
      return redirect(request.referrer)
    name = data['name']
    current_user.add_location(location_id=location_id, name=name)
    flash('Location Saved!')
    return redirect(url_for('home'))

@app.route('/get_locations', methods=['GET'])
def get_locations():
    saved_locations = Location.query.all()
    location_list=[]
    for location in saved_locations:
      temp_dict = {
                    "id": location.id,
                    "name": location.name,
                    "latitude": location.latitude,
                    "longitude": location.longitude
                  }
      location_list.append(temp_dict)
    print(jsonify({"locations": location_list})) if location_list else print('Nothing')
    return jsonify({"locations": location_list})

@app.route('/logout', methods=['GET'])
@jwt_required()
def logout_action():
  flash('Logged Out')
  response = redirect(url_for('login'))
  unset_jwt_cookies(response)
  return response



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
