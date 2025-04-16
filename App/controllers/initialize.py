from .user import create_user, create_admin
from App.database import db
from .location import parse_locations


def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    create_admin('1001','pam', 'pampass')
    parse_locations()