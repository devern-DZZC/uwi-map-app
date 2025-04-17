from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash, url_for, session
from App.controllers import create_user, initialize, get_location, get_user_locations, login_required, get_locations, get_directions
from flask_jwt_extended import current_user, jwt_required
from App.models import RegularUser, Admin
import os
from dotenv import load_dotenv


load_dotenv()
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route("/app", methods=['GET'])
@index_views.route("/app/<int:location_id>", methods=['GET'])
@login_required(RegularUser)
def home(location_id=None):
    route = session.pop('route', None)
    if location_id:
      location = get_location(location_id)
      location_name = location.name
    else:
       location = get_location(1)
       location_name = ""
    return render_template(
        "index.html",
        current_location=location,
        current_user=current_user,
        locations=get_user_locations(current_user.id),
        location_id=location_id,
        location_name = location_name,
        all_locations = get_locations(),
        route = route,
        api_key = GOOGLE_MAPS_API_KEY
    )

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return redirect('/')

@index_views.route('/get-route', methods=['POST'])
def get_route():
    origin = request.form['route1']
    destination = request.form['route2']
    
    route_data = get_directions(origin, destination)
    session['route'] = route_data 
    return  redirect(url_for('index_views.home'))
@index_views.route('/save_location/<int:location_id>', methods=['POST'])
@login_required(RegularUser)
def save_location(location_id):
  data = request.form
  if not data:
    return redirect(request.referrer)
  name = data['name']
  current_user.add_location(location_id=location_id, name=name)
  flash('Location Saved!')
  return redirect('/app')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})