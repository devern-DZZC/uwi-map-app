from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash, url_for, session
from App.controllers import create_user, initialize, get_location, get_user_locations, login_required, get_locations, get_directions, get_locations_by_description
from flask_jwt_extended import current_user, jwt_required, verify_jwt_in_request, get_jwt_identity
from App.models import RegularUser, Admin, Location
import os
from dotenv import load_dotenv


load_dotenv()
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route("/app", methods=['GET'])
@index_views.route("/app/<int:location_id>", methods=['GET'])
def home(location_id=None):
    user = None
    try: 
      verify_jwt_in_request(optional=True)
      identity = get_jwt_identity()
      if identity:
          user = RegularUser.query.get(identity)
    except Exception as e:
        user = None
    route = session.pop('route', None)
    if location_id:
      location = get_location(location_id)
      location_name = location.name
    else:
       location = None
       location_name = ""
    if user: 
      locations = get_user_locations(user.id)
    else:
      locations = []
    return render_template(
        "index.html",
        current_location=location,
        current_user=user,
        locations=locations,
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
@login_required(RegularUser)
def get_route():
    origin = request.form['route1']
    destination = request.form['route2']
    if origin == 'current_location':
        try:
            lat = float(request.form['current_lat'])
            lng = float(request.form['current_lng'])
            origin_coords = f"{lat},{lng}"
        except (ValueError, TypeError):
            flash("Couldn't get current location")
            return redirect(url_for('index_views.home'))
    else:
        location1 = Location.query.get(origin)
        origin_coords = f"{location1.latitude},{location1.longitude}"
    location2 = Location.query.get(destination)
    dest_coords = f"{location2.latitude},{location2.longitude}"
    route_data = get_directions(origin_coords, dest_coords)
    session['route'] = route_data 
    return  redirect(url_for('index_views.home'))

@index_views.route('/save_location/<int:location_id>', methods=['POST'])
@login_required(RegularUser)
def save_location(location_id):
  data = request.form
  if not data:
    return redirect(request.referrer)
  name = data['name']
  result = current_user.add_location(location_id=location_id, name=name)
  if result is True: 
    flash('Location Saved!')
  elif result is False:
    flash('Location already saved')
  else:
    flash('Limit on Saved Locations Reached')  
  return redirect('/app')

@index_views.route('/remove_location/<int:location_id>', methods=['POST'])
@login_required(RegularUser)
def remove_location(location_id):
  result = current_user.delete_location(location_id=location_id)
  if result is True: 
    flash('Location Deleted!')
  else:
     flash('Failed to delete location')
  return redirect('/app')

@index_views.route("/app/filter", methods=["GET"])
@login_required(RegularUser)
def filter_locations():
    description = request.args.get("description")
    filtered_locations = get_locations_by_description(description)
    return render_template(
        "index.html",
        current_location=get_location(1),
        current_user=current_user,
        locations=get_user_locations(current_user.id),
        location_id=None,
        location_name="",
        all_locations=filtered_locations,
        route=None,
        api_key=GOOGLE_MAPS_API_KEY
    )



@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})