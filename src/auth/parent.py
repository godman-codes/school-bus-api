from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import HTTP_200_OK, HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from src.models import db
from src.models.bus import Bus
from src.models.driver import Driver
from src.models.notifications import Notification
from src.models.parent import Parent
from src.models.child import Child
from src.models.attendance import Attendance
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from src.models.trip import ActiveTrip, CompletedTrip, ScheduledTrip
from flasgger import swag_from

parent = Blueprint('parent', __name__, url_prefix='/api/v1/parent')

@parent.post('/login_parent')
@swag_from("../docs/parent/login_parent.yml")
def login_parent():
   
   username = request.json['username']
   password = request.json['password']
   parent = Parent.query.filter_by(username=username).first()
   
   if parent:
      is_pass_correct = check_password_hash(parent.password, password)
      if is_pass_correct:
         refresh = create_refresh_token(identity=parent.id)
         access = create_access_token(identity=parent.id)
         
         return jsonify({
            'message': 'login successfully',
            'parent': {
               'refresh': refresh,
               'access': access,
               'username': parent.username,
               'email': parent.parent_email,
               'phone_number': parent.parent_phone,
               'children': [[x.id, x.first_name, x.last_name] for x in Child.query.filter_by(child_parent=parent.id).all()]
            }
         }), HTTP_200_OK
         
      return jsonify({
         'error': 'Wrong password'
      }), HTTP_401_UNAUTHORIZED
      
   return jsonify({
      'error': 'Wrong username'
   }), HTTP_401_UNAUTHORIZED


@parent.get("/parent_detail")
@jwt_required()
@swag_from("../docs/parent/parent_details.yml")
def parent_details():
   parent_id = get_jwt_identity()
   parents = Parent.query.filter_by(id=parent_id).first()
   return jsonify({
      'parent': {
         'parent_first_name': parents.first_name,
         'parent_last_name': parents.last_name,
         'parent_username': parents.username,
         'parent_email': parents.parent_email,
         'parent_phone': parents.parent_phone,
         'children': [[x.id, x.first_name, x.last_name, x.child_class, x.child_routes] for x in Child.query.filter_by(child_parent=parent_id).all()]
         }
   }), HTTP_200_OK


@parent.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
   identity = get_jwt_identity()
   access = create_access_token(identity=identity)
   return jsonify({
      'access': access
   }), HTTP_200_OK


@parent.put('/change_password')
@jwt_required()
@swag_from("../docs/admin_auth/change_password.yml")
def change_password():
   parent_id = get_jwt_identity()
   old_password = request.json['old_password']
   new_password = request.json['new_password']
   parents = Parent.query.filter_by(id=parent_id).first()
   is_pass = check_password_hash(parents.password, old_password)
   if is_pass:
      if len(new_password) < 6:
         return jsonify({
            'error': 'password is too short'
            }), HTTP_400_BAD_REQUEST
      parents.password = generate_password_hash(new_password)
      db.session.commit()
      return jsonify({
         'message': 'password changed successfully'
         }), HTTP_200_OK
   return jsonify({'error': 'password is invalid'}), HTTP_401_UNAUTHORIZED


@parent.get('/get_children_Completed_trip/<int:id>')
@jwt_required()
@swag_from("../docs/parent/get_child_trip.yml")
def get_children_Completed_trip(id):
   current_user = get_jwt_identity()
   child = Child.query.filter_by(child_parent=current_user, id=id).first()
   trip = CompletedTrip.query.filter_by(routes=child.child_routes).first()
   bus = Bus.query.filter_by(bus_id=trip.bus_id).first()
   driver = Driver.query.filter_by(id=bus.bus_driver).first()
   return jsonify({
      'trip': {
         'routes': trip.routes,
         'date': trip.date,
         'start_timestamp': trip.start_timestamp,
         'latest_gps': trip.latest_gps
      },
      'bus': {
         'id': bus.id,
         'bus_name': bus.bus_name,
         'plate_number': bus.plate_number,
         'driver': {
            'first_name': driver.first_name,
            'last_name': driver.last_name,
            'driver_phone': driver.driver_phone
         }
      }
   }), HTTP_302_FOUND

@parent.get('/get_scheduled_child_trip/<int:id>')
@jwt_required()
def get_scheduled_child_trip(id):
   current_user = get_jwt_identity()
   children = Child.query.filter_by(child_parent=current_user).first()
   if children is None:
      return jsonify({'error': 'No children'}), HTTP_404_NOT_FOUND
   trip = ActiveTrip.query.filter_by(id=id).first()
   if trip is None:
      return({'error': 'You can\'t track trip because it is not yet active'}), HTTP_400_BAD_REQUEST
   bus = Bus.query.filter_by(bus_id=trip.bus_id).first()
   if bus is None:
      return jsonify({'error': 'No bus found'}), HTTP_404_NOT_FOUND
   driver = Driver.query.filter_by(id=bus.bus_driver).first()
   if driver is None:
      return jsonify({'error': 'No driver found'}), HTTP_404_NOT_FOUND
   return jsonify({
      'message': 'success',
      'trip': {
         'id': trip.id,
         'date': trip.date,
         'start_timestamp': trip.start_timestamp,
         'latest_gps': trip.latest_gps,
         'last_updated_timestamp': trip.last_updated_timestamp,
         'routes': trip.routes,
         'bus_plate_number': bus.plate_number,
         'bus_name': bus.bus_name,
         'driver': f'Mr {driver.last_name}',
         'driver_phone': driver.driver_phone
      }
      }), HTTP_302_FOUND


@parent.get('/get_scheduled_children_trip')
@jwt_required()
def get_scheduled_children_trip():
   current_user = get_jwt_identity()
   children = Child.query.filter_by(child_parent=current_user).all()
   print('amy')
   if len(children) == 0:
      return jsonify({'error': 'No children'}), HTTP_400_BAD_REQUEST
   children_routes = [x.child_routes for x in children]
   trip = ScheduledTrip.query.filter_by(routes=children_routes[0]).all()
   if len(trip) == 0:
      return jsonify({'error': 'No scheduled trip'}), HTTP_400_BAD_REQUEST
   scheduled_trips = []
   for i in trip:
      scheduled_trips.append({
         'id': i.id,
         'date': i.date,
         'start_timestamp': i.start_timestamp,
         'latest_gps': i.latest_gps,
         'last_updated_timestamp': i.last_updated_timestamp,
         'routes': i.routes,
      })
   return jsonify({
      'message': 'success',
      'children_scheduled_trips': scheduled_trips
      }), HTTP_302_FOUND


@parent.get('/get_child_active_trip/<int:id>')
@jwt_required()
def get_children_active_trip(id):
   """
   passing the child id to get the active trip from the attendance table
   """
   current_user = get_jwt_identity()
   child = Child.query.filter_by(id=id, child_parent=current_user).first()
   if child is None:
      return jsonify({'error': 'you are not authorized to view child details'}), HTTP_400_BAD_REQUEST
   attendances = Attendance.query.filter_by(child_id=id).first()
   if attendances is None:
      return jsonify({'error': 'child is not on any ongoing trip'}), HTTP_400_BAD_REQUEST
   if attendances.is_pick_present == True and attendances.is_drop_present == True:
      return jsonify({'error': 'child has completed the trip'}), HTTP_400_BAD_REQUEST
   trip = ActiveTrip.query.filter_by(id=attendances.trip_id).first()
   bus = Bus.query.filter_by(bus_id=trip.bus_id).first()
   driver = Driver.query.filter_by(id=bus.bus_driver).first()
   return jsonify({
      'id': trip.id,
      'bus_name': bus.bus_name,
      'plate_number': bus.plate_number,
      'is_active': bus.is_active,
      'driver': f'Mr {driver.first_name}',
      'driver_phone': driver.driver_phone
      }), HTTP_302_FOUND

@parent.get('/get_notifications')
@jwt_required()
@swag_from("../docs/parent/get_notifications.yml")
def get_notification():
   current_user = get_jwt_identity()
   notifications = Notification.query.filter_by(parent=current_user).all()
   if notifications is None:
      return jsonify({'error': 'There are no notifications for you'}), HTTP_400_BAD_REQUEST
   notify = {}
   for i in notifications:
      notify[i.id] = {
         'message': i.message,
         'time': i.time
      }
   return jsonify(notify), HTTP_302_FOUND

# @parent.delete('/delete_notification/<int:id>')
# @jwt_required()
# def get_notification(id):
#    current_user = get_jwt_identity()
#    notification = Notification.query.filter_by(id=id, parent=current_user).first()
#    if not notification:
#       return jsonify({
#          'error': 'notification not found'
#       }), HTTP_404_NOT_FOUND
#    db.session.delete(notification)
#    db.session.commit()
#    return jsonify({'message': 'deleted'}), HTTP_204_NO_CONTENT



# @parent.get('/get_children_trip')
# @jwt_required()
# def get_children_trip():
#    current_user = get_jwt_identity()
#    children = Child.query.filter_by(child_parent=current_user).all()
#    if children is None:
#       return jsonify({'error': 'No children'}), HTTP_400_BAD_REQUEST
#    trip = Trip.query.all()
#    bus = Bus.query.all()
#    driver = Driver.query.all()
#    kids = []
#    for i in children:
#       trips = []
#       buses = []
#       drivers = []
#       for j in trip:
#          if j.routes == i.child_routes:
#             trips.append({
#                'id': j.id, 
#                'routes': j.routes,
#                'bus_id': j.bus_id,
#                'date': j.date
#             })
#       for t in trips:
#          for p in bus:
#             if p.bus_id == t['bus_id']:
#                buses.append({
#                   'trip_id': t['id'],
#                   'bus_name': p.bus_name,
#                   'plate_number': p.plate_number,
#                   'active': p.is_active,
#                   'bus_driver': p.bus_driver
#                })
#       for b in buses:
#          for d in driver:
#             if d.id == b['bus_driver']:
#                drivers.append({
#                   'trip_id': b['trip_id'],
#                   'first_name': f'Mr {d.first_name}',
#                   'driver_phone': d.driver_phone
#                })
#       kids.append({
#          'id': i.id,
#          'first_name': i.first_name,
#          'trip': trips,
#          'bus': buses,
#          'driver': drivers
         
#       })
#    return jsonify({
#       'message': 'success',
#       'children': kids
#       }), HTTP_302_FOUND