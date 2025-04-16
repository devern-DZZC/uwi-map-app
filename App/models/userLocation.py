from App.database import db

class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    marker_name = db.Column(db.String(50), nullable=False)
    
    user = db.relationship('RegularUser', back_populates='locations')
    location = db.relationship('Location', back_populates='user_locations')

    def __init__(self, user_id, location_id, marker_name):
        self.user_id = user_id
        self.location_id = location_id
        self.marker_name = marker_name