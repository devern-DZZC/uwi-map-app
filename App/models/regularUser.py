from App.database import db
from .user import User
from .location import Location
from .userLocation import UserLocation

class RegularUser(User):
  __tablename__ = 'regular_user'
  locations = db.relationship('UserLocation', back_populates='user', cascade='all, delete-orphan')
  __mapper_args__ = {
        'polymorphic_identity': 'regular'
    }
 

  def add_location(self, location_id, name):
      existing_locations = UserLocation.query.filter_by(user_id=self.id).count()
      if existing_locations >= 10:
        return 'limit_reached'
      location = Location.query.filter_by(id=location_id).first()
      if location:
        try:
          saved_location = UserLocation.query.filter_by(user_id=self.id, location_id=location.id).first()
          if saved_location is None:
            user_location = UserLocation(user_id=self.id, location_id=location.id, marker_name=name)
            db.session.add(user_location)
            db.session.commit()
            return True
          else:
              return False
        except Exception as e:
          print(e)
          db.session.rollback()
          return None
      return None
  
  def delete_location(self, location_id):
      user_location = UserLocation.query.filter_by(user_id=self.id, location_id=location_id).first()
      if user_location:
        try: 
          db.session.delete(user_location)
          db.session.commit()
          return True
        except Exception as e:
          print(e)
          db.session.rollback()
          return None
      return None
         

  
 
