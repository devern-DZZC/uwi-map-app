from App.models import UserLocation, Location, RegularUser
from App.database import db

def get_user_locations(user_id):
    user = RegularUser.query.get(user_id)
    if user:
        return UserLocation.query.filter_by(user_id=user_id).all()
    return f'{user_id} user not found'