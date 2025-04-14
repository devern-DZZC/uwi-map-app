from flask import Blueprint, jsonify, request,flash
from App.controllers import get_locations, login_required, add_location
from App.models import Admin

location_views = Blueprint('location_views', __name__, template_folder='../templates')

@location_views.route('/get_locations', methods=['GET'])
def get_all_locations():
    locations = get_locations()
    return jsonify({"locations": locations})

@location_views.route('/add_location', methods=['POST'])
@login_required(Admin)
def add_new_location():
  data = request.get_json()
  try:
    add_location(name=data['name'], lat=data['latitude'], lon=data['longitude'], description=data['building_type'])
    flash('Location Added Successfully!')
    return jsonify({'success': True})
  except:
    return jsonify({'success': False, 'message': 'Location already exists at these coordinates.'})