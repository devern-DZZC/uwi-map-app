from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import get_location, get_user_locations, admin_required, login_required, get_location,update_location_by_id, delete_location_by_id
from flask_jwt_extended import current_user, jwt_required
import os
from dotenv import load_dotenv
from App.models import Admin
from App.database import db

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

@admin_views.route('/admin')
@login_required(Admin)
def admin():
  return render_template('admin.html', api_key = GOOGLE_MAPS_API_KEY)

@admin_views.route('/admin/update_location/<int:loc_id>', methods=['POST'])
@login_required(Admin)
def update_location(loc_id):
  data = request.get_json()
  name = data.get('name')
  building_type = data.get('building_type')
  updated_location, error = update_location_by_id(loc_id, name, building_type)
  if error:
    flash("Error updating location: ")
    return jsonify({'success': False, 'message': error}), 500 if updated_location else 404
  flash("Location updated successfully.")
  return jsonify({'success': True})

@admin_views.route('/admin/delete_location/<int:loc_id>', methods=['DELETE'])
@login_required(Admin)
def delete_location(loc_id):
  success, error = delete_location_by_id(loc_id)
  if not success:
    flash("Error deleting location: ")
    return jsonify({'success': False, 'message': error}), 500 if error != "Location not found" else 404
  flash("Location deleted successfully.")
  return jsonify({'success': True})
