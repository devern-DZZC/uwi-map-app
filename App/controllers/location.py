from App.models import Location, RegularUser
from App.database import db
import csv

def add_location(name, lat, lon, description):
    try:
        new_location = Location(
            name=name,
            description=description,
            latitude=lat,
            longitude=lon,
        )
        db.session.add(new_location)
        db.session.commit()
        return new_location
    except:
        return None
    
def get_location(loc_id):
    location = Location.query.get(loc_id)
    return location
    
def get_locations():
    saved_locations = Location.query.all()
    location_list=[]
    for location in saved_locations:
        temp_dict = {
                        "id": location.id,
                        "name": location.name,
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    }
        location_list.append(temp_dict)
    return location_list

def parse_locations():
    with open('locations.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        locations = []
        
        for row in csv_reader:
            name = row[0]  
            c = row[1]     
            building_type = row[2]

            coords = c.split(', ')
            lat, lon = float(coords[0]), float(coords[1])
            
            if lon is not None and lat is not None:
                location = Location(name=name, latitude=lat, longitude=lon, description=building_type)
                locations.append(location)

        db.session.add_all(locations)
        db.session.commit()


def update_location_by_id(loc_id, name, building_type):
    location = get_location(loc_id)
    if not location:
        return None, "Location not found"
    location.name = name
    location.description = building_type
    try:
        db.session.commit()
        return location, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def delete_location_by_id(loc_id):
    location = get_location(loc_id)
    if not location:
        return None, "Location not found"
    try:
        db.session.delete(location)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)