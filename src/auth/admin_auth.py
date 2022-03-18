from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from flask import Blueprint, jsonify, request
import validators
from src.models.admin import School
from werkzeug.security import check_password_hash, generate_password_hash
from src.models import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

admin_auth = Blueprint('admin_auth', __name__, url_prefix="/api/v1/admin_auth")

@admin_auth.post('/register_school')
def register_school():

   school_name = request.json['school_name']
   school_location = request.json['school_location']
   school_website = request.json['school_website']
   school_email = request.json['school_email']
   school_admin_id = request.json['school_admin_id']
   school_admin_password = request.json['school_admin_password']

   if not school_name or len(school_name) < 2:
      return jsonify({'error': 'Enter a valid school name'}), HTTP_400_BAD_REQUEST

   if not school_location or len(school_location) < 2:
      return jsonify({'error': 'Enter a valid school location'}), HTTP_400_BAD_REQUEST 

   if not school_website or len(school_website) < 2:
      return jsonify({'error': 'Enter a valid school website'}), HTTP_400_BAD_REQUEST     

   if len(school_admin_password) < 6:
      return jsonify({'error': 'password is too short'}), HTTP_400_BAD_REQUEST

   if len(school_admin_id) < 7:
      return jsonify({'error': 'Admin Id too short'}), HTTP_400_BAD_REQUEST

   if " " in (school_admin_id):
      return jsonify({'error': 'Admin Id should contain no spaces'}), HTTP_400_BAD_REQUEST

   if not validators.email(school_email):
      return jsonify({'error': 'Email is not valid'}), HTTP_400_BAD_REQUEST

   if not validators.url(school_website):
      return jsonify({'error': 'Enter a valid school website'}), HTTP_400_BAD_REQUEST

   if School.query.filter_by(school_name=school_name).first() is not None:
      return jsonify({'error': 'This school name already exist'})
   
   if School.query.filter_by(school_email=school_email).first() is not None:
      return jsonify({'error': 'Email belongs to another school'}), HTTP_400_BAD_REQUEST

   if School.query.filter_by(school_admin_id=school_admin_id).first() is not None:
      return jsonify({'error': 'id unavailable'}), HTTP_400_BAD_REQUEST

      
   pwd_hash = generate_password_hash(school_admin_password)

   school = School(
      school_admin_id=school_admin_id,
      school_admin_password=pwd_hash,
      school_location=school_location,
      school_email=school_email,
      school_website=school_website,
      school_name=school_name      
      )


   db.session.add(school)
   db.session.commit()

   return jsonify({'message': f'Welcome to Godman school transport {school_name}',
                  'user': {
                     'school_name': school_name,
                     'school_location': school_location,
                     'school_email': school_email,
                     'school_website': school_website
                  }
                  }), HTTP_201_CREATED


@admin_auth.post('/login_admin')
def login_admin():
   school_admin_id = request.json['admin_id']
   password = request.json['password']

   user = School.query.filter_by(school_admin_id=school_admin_id).first()

   if user:
      is_pass_correct = check_password_hash(user.school_admin_password, password)
      if is_pass_correct:
         refresh = create_refresh_token(identity=user.id)
         access = create_access_token(identity=user.id)

         return jsonify({
            'message': 'login successfull',
            'admin':{
               'refresh': refresh,
               'access': access,
               'school_name': user.school_name,
               'school_location': user.school_location,
               'school_email': user.school_email,
               'school_website': user.school_website
            }
         }), HTTP_200_OK

   return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

@admin_auth.get("/admin_details")
@jwt_required()
def admin_details():
   user_id = get_jwt_identity()
   user = School.query.filter_by(id=user_id).first()
   return jsonify({
      'user': {
         'school_name': user.school_name,
         'school_location': user.school_location,
         'school_email': user.school_email,
         'school_website': user.school_website
         }
   }), HTTP_200_OK


@admin_auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
   identity = get_jwt_identity()
   access = create_access_token(identity=identity)
   return jsonify({
      'access': access
   }), HTTP_200_OK
   