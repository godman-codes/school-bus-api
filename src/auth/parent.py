from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from src.models.parent import Parent
from src.models.child import Child
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

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
   
   