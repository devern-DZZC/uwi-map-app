from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, flash
from App.controllers import get_location, get_user_locations, admin_required, login_required, get_location
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
  location = get_location(loc_id)
  if not location:
    flash("Location not found.")
    return jsonify({'success': False, 'message': 'Location not found'}), 404
  data = request.get_json()
  location.name = data['name']
  location.description = data['building_type']
  try:
    db.session.commit()
    flash("Location updated successfully.")
    return jsonify({'success': True})
  except Exception as e:
    db.session.rollback()
    flash("Error updating location.")
    return jsonify({'success': False, 'message': str(e)}), 500
  
@admin_views.route('/admin/delete_location/<int:location_id>', methods=['DELETE'])
@login_required(Admin)
def delete_location(location_id):
  location = get_location(location_id)
  if not location:
    flash("Location not found.")
    return jsonify({'success': False, 'message': 'Location not found'}), 404
  try:
    db.session.delete(location)
    db.session.commit()
    flash("Location deleted successfully.", "success")
    return jsonify({'success': True})
  except Exception as e:
    db.session.rollback()
    flash("Error deleting location.")
    return jsonify({'success': False, 'message': str(e)}), 500
