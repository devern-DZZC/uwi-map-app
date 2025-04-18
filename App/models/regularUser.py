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
      location = Location.query.filter_by(id=location_id).first()
      if location:
        try:
          saved_location = UserLocation.query.filter_by(user_id=self.id, location_id=location.id).first()
          if saved_location is None:
            userLocation = UserLocation(user_id=self.id, location_id=location.id, marker_name=name)
            db.session.add(userLocation)
            db.session.commit()
          else:
              return False
          return True
        except Exception as e:
          print(e)
          db.session.rollback()
          return None
      return None
  
 
