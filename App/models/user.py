from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'user', 'polymorphic_on': type}

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    
class RegularUser(User):
  __tablename__ = 'regular_user'
  locations = db.relationship('UserLocation', back_populates='user')
  __mapper_args__ = {
      'polymorphic_identity': 'regular user',
  }

  def add_location(self, location_id, name):
      location = Location.query.filter_by(id=location_id).first()
      if location:
        try:
          userLocation = UserLocation(user_id=self.id, location_id=location.id, marker_name=name)
          db.session.add(userLocation)
          db.session.commit()
          return userLocation
        except Exception as e:
          print(e)
          db.session.rollback()
          return None
      return None

class Admin(User):
    __tablename__ = 'admin'
    staff_id = db.Column(db.String(120), unique=True)
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __init__(self, staff_id, username, password):
        super().__init__(username, password)
        self.staff_id = staff_id

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(120), nullable=False)

    users = db.relationship('UserLocation', back_populates='location')

    def __init__(self, name, longitude, latitude, description):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.description=description

class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    marker_name = db.Column(db.String(50), nullable=False)
    
    user = db.relationship('RegularUser', back_populates='locations')
    location = db.relationship('Location', back_populates='users')

    def __init__(self, user_id, location_id, marker_name):
        self.user_id = user_id
        self.location_id = location_id
        self.marker_name = marker_name
