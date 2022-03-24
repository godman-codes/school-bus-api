from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from src.models import db
from src.models.bus import Bus
from src.models.driver import Driver
from src.models.notifications import Notification
from src.models.parent import Parent
from src.models.child import Child
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

from src.models.trip import Trip

parent = Blueprint('parent', __name__, url_prefix='/api/v1/parent')

@parent.post('/login_parent')
def login_parent():
   
   username = request.json['username']
   password = request.json['password']
   # print('man')
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



# @parent.get('/get_child-detail')
# @jwt_required()
# def get_child_details():
#    current_user = get_jwt_identity()
#    child = Child.query.filter_by(child_parent=current_user).all()
#    if child is None:
#       return jsonify({})
#    child_obj = {}




@parent.get('/get_child_trip/<int:id>')
@jwt_required()
def get_child_trip(id):
   current_user = get_jwt_identity()
   child = Child.query.filter_by(child_parent=current_user, id=id).first()
   trip = Trip.query.filter_by(routes=child.child_routes).first()
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


@parent.get('/get_notifications')
@jwt_required()
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
#          'error': 'nottification not found'
#       }), HTTP_404_NOT_FOUND
#    db.session.delete(notification)
#    db.session.commit()
#    return jsonify({'message': 'deleted'}), HTTP_204_NO_CONTENT