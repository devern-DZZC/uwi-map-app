from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.controllers import create_user, initialize, get_location, get_user_locations, admin_required, login_required
from flask_jwt_extended import current_user, jwt_required
import os
from dotenv import load_dotenv
from App.models import Admin

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

@admin_views.route('/admin')
@login_required(Admin)
def admin():
  return render_template('admin.html', api_key = GOOGLE_MAPS_API_KEY)