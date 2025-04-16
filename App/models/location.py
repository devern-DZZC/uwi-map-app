from App.database import db
from sqlalchemy import UniqueConstraint

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='unique_lat_lng'),
    )
    user_locations = db.relationship('UserLocation', back_populates='location', cascade='all, delete-orphan')

    def __init__(self, name, longitude, latitude, description):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.description=description