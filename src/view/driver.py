from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.attendance import Attendance
from src.models.child import Child
from src.models.driver import Driver
from src.constants.http_status_codes import HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from src.models import db
from src.models.routes import Routes
from src.models.trip import Trip
from src.models.bus import Bus

driver = Blueprint('driver', __name__, url_prefix="/api/v1/driver")

@driver.post('/login_driver')
def login_driver():

   driver_id = request.json['driver_id']
   password = request.json['password']

   drivers = Driver.query.filter_by(driver_id=driver_id).first()
   
   if drivers:
      
      is_pass_correct = check_password_hash(drivers.password, password)
      
      if is_pass_correct:
         refresh = create_refresh_token(identity=drivers.id)
         access = create_access_token(identity=drivers.id)

         return jsonify({
            'message': 'log in successful',
            'driver': {
               'access': access,
               'refresh': refresh,
         'first_name': drivers.first_name,
         'last_name': drivers.last_name,
         'driver_id': drivers.driver_id,
         'driver_email': drivers.driver_email,
         'driver_phone': drivers.driver_phone
         }
         }), HTTP_200_OK
         
         
      return jsonify({'error': 'password is invalid'}), HTTP_401_UNAUTHORIZED

   return jsonify({'error': 'invalid driver_id'}), HTTP_401_UNAUTHORIZED


@driver.get("/get_drivers_trips")
@jwt_required()
def get_drivers_Bus():
   current_user = get_jwt_identity()

   drivers_bus = Bus.query.filter_by(id=current_user).first()

   if drivers_bus:
      return jsonify({
         'bus_name': drivers_bus.bus_name,
         'plate_number': drivers_bus.plate_number,
         'bus_id': drivers_bus.bus_id,
         'capacity': drivers_bus.capacity,
         'initial_attendance': drivers_bus.initial_attendance,
         'is_active': drivers_bus.is_active
                     }), HTTP_302_FOUND
   return jsonify({'error': 'no bus allocated to driver'}), HTTP_404_NOT_FOUND  

@driver.get("/get_trips")
@jwt_required()
def get_trips():

   current_user = get_jwt_identity()

   drivers_bus = Bus.query.filter_by(id=current_user).first()

   if drivers_bus:
      trips = Trip.query.filter_by(bus_id=drivers_bus.bus_id).first()

      if trips:
         return jsonify({
            'trip': {
               'routes': f'Route {trips.routes}',
         'bus_id': trips.bus_id,
         'date': trips.date,
         'start_time_stamp': trips.start_timestamp,
         'end_time_stamp': trips.end_timestamp,
         'latest_gps': trips.latest_gps,
         'last_update_timestamp': trips.last_update_timestamp
            }
         })


@driver.get("/driver_detail")
@jwt_required()
def driver_details():
   driver_id = get_jwt_identity()
   driver = Driver.query.filter_by(id=driver_id).first()
   driver_bus = Bus.query.filter_by(bus_driver=driver_id).all()
   driver_trip = Trip.query.filter_by(bus_id=driver_bus[0].bus_id).all()
   return jsonify({
      'driver': {
         'driver_first_name': driver.first_name,
         'driver_last_name': driver.last_name,
         'driver_id': driver.driver_id,
         'driver_email': driver.driver_email,
         'driver_phone': driver.driver_phone,
         'bus': [[x.id, x.bus_name, x.plate_number] for x in driver_bus],
         'trips': [[x.id, x.routes, x.bus_id, x.date] for x in driver_trip]
         }
   }), HTTP_200_OK


@driver.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
   identity = get_jwt_identity()
   access = create_access_token(identity=identity)
   return jsonify({
      'access': access
   }), HTTP_200_OK
   


@driver.post('/start_trip')
@jwt_required()
def start_trip():
   
   current_user = get_jwt_identity()
   drivers = Bus.query.filter_by(bus_driver=current_user).first()
   trips = Trip.query.filter_by(bus_id=drivers.bus_id).first()
   if trips.start_timestamps:
      return jsonify({
         'error': 'this trip has already been started'
      })

   start_timestamp = trips.start_timestamps()
   make_active = drivers.activate_bus()
   

   return jsonify({
      'message': 'trip has started',
      'trip': {
         'trip_date': trips.date,
         'start_timestamp': start_timestamp,
         'is_active': make_active,
         'routes': trips.routes,
         'bus_id': trips.bus_id
      }
      }), HTTP_200_OK   

@driver.put('/change_password')
@jwt_required()
def change_password():
   driver_id = get_jwt_identity()
   old_password = request.json['old_password']
   new_password = request.json['new_password']
   drivers = Driver.query.filter_by(id=driver_id).first()
   is_pass = check_password_hash(drivers.password, old_password)
   if is_pass:
      if len(new_password) < 6:
         return jsonify({
            'error': 'password is too short'
            }), HTTP_400_BAD_REQUEST
      drivers.password = generate_password_hash(new_password)
      db.session.commit()
      return jsonify({
         'message': 'password changed successfully'
         }), HTTP_200_OK
   return jsonify({'error': 'password is invalid'}), HTTP_401_UNAUTHORIZED

@driver.post('/child_picked_attendance')
@jwt_required()
def child_picked_attendance():
   drivers = get_jwt_identity()
   child_first_name = request.json['first_name']
   child_last_name = request.json['last_name']
   child_parent = request.json['parent']
   bus_gps = request.json['bus_gps']
   # if child_first_name or child_last_name or child_parent == '':
   #    return({'error': 'enter valid child'}), HTTP_404_NOT_FOUND
   child = Child.query.filter_by(first_name=child_first_name, last_name=child_last_name, child_parent=child_parent).first()
   child_trip = Trip.query.filter_by(routes=child.child_routes).first()
   trip_bus = Bus.query.filter_by(bus_driver=drivers).first()
   if trip_bus.is_active != True:
      return jsonify({'error': 'Bus is not active'}), HTTP_400_BAD_REQUEST
   attendance = Attendance(
      child_id=child.id,
      trip_id=child_trip.id,
   )
   db.session.add(attendance)
   db.session.commit()
   attendance = Attendance.query.filter_by(child_id=child.id, trip_id=child_trip.id).first()
   attendance.picked(bus_gps)
   return jsonify({'message': 'attendance taken'}), HTTP_200_OK
   