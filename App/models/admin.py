from App.database import db
from .user import User

class Admin(User):
    __tablename__ = 'admin'
    staff_id = db.Column(db.String(120), unique=True)
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def __init__(self, staff_id, username, password):
        super().__init__(username, password)
        self.staff_id = staff_id