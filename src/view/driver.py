from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from src.models.driver import Driver
from src.constants.http_status_codes import HTTP_302_FOUND, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
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
         
         
      return jsonify({'error': 'password id invalid'}), HTTP_401_UNAUTHORIZED

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
