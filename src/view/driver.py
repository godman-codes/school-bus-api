from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.attendance import Attendance
from src.models.child import Child
from src.models.driver import Driver
from src.constants.http_status_codes import HTTP_201_CREATED, HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from src.models import db
from src.models.notifications import Notification
from src.models.trip import Trip
from src.models.bus import Bus
from src.models.location import Location
from flasgger import swag_from

driver = Blueprint('driver', __name__, url_prefix="/api/v1/driver")

@driver.post('/login_driver')
@swag_from("../docs/driver/login_driver.yml")
def login_driver():
   body = request.get_json('data')

   driver_id = body['driver_id']
   password = body['password']

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


@driver.get("/get_drivers_bus")
@jwt_required()
@swag_from("../docs/driver/get_drivers_bus.yml")
def get_drivers_Bus():
   current_user = get_jwt_identity()

   drivers_bus = Bus.query.filter_by(id=current_user).first()

   if drivers_bus is None:
      return({'message': 'there is no bus assigned to you contact admin for more details'}), HTTP_400_BAD_REQUEST

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
@swag_from("../docs/driver/get_trips.yml")
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
         }), HTTP_302_FOUND
      else:
         return jsonify({'message': 'you have no trips contact admin for more info'}), HTTP_400_BAD_REQUEST
   else:
      return jsonify({'message': 'there is no bus assigned to you contact admin for more details'}), HTTP_400_BAD_REQUEST


@driver.get("/driver_detail")
@jwt_required()
@swag_from("../docs/driver/driver_detail.yml")
def driver_detail():
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
@swag_from("../docs/driver/start_trip.yml")
def start_trip():
   
   current_user = get_jwt_identity()
   drivers = Bus.query.filter_by(bus_driver=current_user).first()
   trips = Trip.query.filter_by(bus_id=drivers.bus_id).first()
   if trips.start_timestamp:
      return jsonify({
         'error': 'this trip has already been started'
      }), HTTP_400_BAD_REQUEST
   gps = Location.query.filter_by(trip_id=trips.id).first()
   if gps is None:
      return jsonify({'error': 'get location first'}), HTTP_401_UNAUTHORIZED
   start_timestamp = trips.start_timestamps()
   make_active = drivers.activate_bus()
   latest_gps = trips.get_latest_gps(gps.gps)
   notification = Notification(
      message=f'{drivers.bus_id} has started its trip',
      driver=drivers.bus_driver
   )
   db.session.add(notification)
   db.session.commit()
   return jsonify({
      'message': 'trip has started',
      'trip': {
         'trip_date': trips.date,
         'start_timestamp': start_timestamp,
         'is_active': make_active,
         'routes': trips.routes,
         'bus_id': trips.bus_id,
         'latest_gps': latest_gps
      }
      }), HTTP_200_OK   

@driver.put('/change_password')
@jwt_required()
@swag_from("../docs/admin_auth/change_password.yml")
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



@driver.post('/get_location')
@jwt_required()
@swag_from("../docs/driver/get_location.yml")
def get_location():
   location = request.json['location']
   driver_id = get_jwt_identity()

   if location is None:
      return jsonify({
         'error': 'location is invalid'
      }), HTTP_400_BAD_REQUEST
   bus = Bus.query.filter_by(bus_driver=driver_id).first()
   if not bus:
      return jsonify({'error': 'You were not assigned a bus'}), HTTP_400_BAD_REQUEST
   trip = Trip.query.filter_by(bus_id=bus.bus_id).first()
   if not trip:
      return jsonify({'error': 'this bus not assigned any trip'}), HTTP_400_BAD_REQUEST
   current_time = datetime.now()
   trip.lastest_gps = location
   trip.last_update_timestamp = current_time
   existing_location = Location.query.filter_by(trip_id=trip.id).first()
   if existing_location:
      existing_location.update_location(location)
      existing_location.get_times_stamp()
      return jsonify({
      'message': 'successfully updated',
      'location': {
         'location_id': existing_location.id,
         'times_stamp': existing_location.times_stamp,
         'gps': existing_location.gps,
         'trip': {
            'trip_id': trip.id,
            'routes': trip.routes,
            'date': trip.date,
            'started': trip.start_timestamp,
            'last_update': current_time
         },
         'bus': {
            'plate_number': bus.plate_number,
            'bus_id': bus.bus_id
         }
      }
   }), HTTP_200_OK
   locations = Location(gps=location,
                        times_stamp=current_time,
                        trip_id=trip.id
                        )
   
   db.session.add(locations)
   db.session.commit()

   return jsonify({
      'message': 'success',
      'location': {
         'location_id': locations.id,
         'times_stamp': locations.times_stamp,
         'gps': locations.gps,
         'trip': {
            'trip_id': trip.id,
            'routes': trip.routes,
            'date': trip.date,
            'started': trip.start_timestamp,
            'last_update': current_time

         },
         'bus': {
            'plate_number': bus.plate_number,
            'bus_id': bus.bus_id
         }
      }
   }), HTTP_201_CREATED

@driver.post('/child_picked_attendance')
@jwt_required()
@swag_from("../docs/driver/child_picked_attendance.yml")
def child_picked_attendance():
   drivers = get_jwt_identity()
   child_first_name = request.json['first_name']
   child_last_name = request.json['last_name']
   child_parent = request.json['parent']
   if not child_first_name or not child_last_name:
      return({'error': 'enter valid child'}), HTTP_404_NOT_FOUND
   child = Child.query.filter_by(first_name=child_first_name, last_name=child_last_name, child_parent=child_parent).first()
   child_trip = Trip.query.filter_by(routes=child.child_routes).first()
   trip_bus = Bus.query.filter_by(bus_driver=drivers).first()
   bus_location = Location.query.filter_by(trip_id=child_trip.id).first()
   if trip_bus.is_active != True:
      return jsonify({'error': 'Bus is not active'}), HTTP_400_BAD_REQUEST
   attendance = Attendance(
      child_id=child.id,
      trip_id=child_trip.id,
   )
   notification = Notification(
      message=f'{child_first_name} just entered the school bus',
      child=child.id,
      parent=child_parent
      )
   db.session.add(attendance)
   db.session.add(notification)
   db.session.commit()
   # attendance = Attendance.query.filter_by(child_id=child.id, trip_id=child_trip.id).first()

   attendance.picked(bus_location.gps)
   return jsonify({'message': 'picked attendance taken'}), HTTP_200_OK


@driver.put('/child_drop_attendance')
@jwt_required()
@swag_from("../docs/driver/child_drop_attendance.yml")
def child_drop_attendance():
   drivers = get_jwt_identity()
   child_first_name = request.json['first_name']
   child_last_name = request.json['last_name']
   child_parent = request.json['parent']
   
   child = Child.query.filter_by(first_name=child_first_name, last_name=child_last_name, child_parent=child_parent).first()
   child_trip = Trip.query.filter_by(routes=child.child_routes).first()
   trip_bus = Bus.query.filter_by(bus_driver=drivers).first()
   bus_location = Location.query.filter_by(trip_id=child_trip.id).first()
   if trip_bus.is_active != True:
      return jsonify({'error': 'Bus is not active'}), HTTP_400_BAD_REQUEST
   attendance = Attendance.query.filter_by(child_id=child.id).first()
   if attendance is None:
      return jsonify({'error': 'this child was not picked'}), HTTP_404_NOT_FOUND
   notification = Notification(
      message=f'{child_first_name} just got to your destination',
      child=child.id,
      parent=child_parent
      )
   db.session.add(notification)
   attendance.dropped(bus_location.gps)
   return jsonify({'message': 'drop attendance taken'}), HTTP_200_OK

@driver.post('/end_trip')
@jwt_required()
@swag_from("../docs/driver/end_trip.yml")
def end_trip():
   current_user = get_jwt_identity()
   drivers = Bus.query.filter_by(bus_driver=current_user).first()
   trips = Trip.query.filter_by(bus_id=drivers.bus_id).first()
   if trips.end_timestamp:
      return jsonify({
         'error': 'this trip has already been ended'
      }), HTTP_400_BAD_REQUEST
   
   end_timestamp = trips.end_timestamps()
   make_active = drivers.deactivate_bus()
   notification = Notification(
      message=f'{drivers.bus_id} has ended its trip',
      driver=f'{drivers.bus_driver}'
   )
   db.session.add(notification)
   db.session.commit()
   return jsonify({
      'message': 'trip was ended successfully',
      'trip': {
         'trip_date': trips.date,
         'start_timestamp': trips.start_timestamp,
         'end_timestamp': end_timestamp,
         'is_active': make_active,
         'routes': trips.routes,
         'bus_id': trips.bus_id,
         'latest_gps': trips.latest_gps
      }
      }), HTTP_200_OK   


