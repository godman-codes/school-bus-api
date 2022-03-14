from email import message
import json
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from src.models.admin import School
from src.models.parent import Parent
from src.models import db
from src.helper.parentHelpers import create_parent_username

admin = Blueprint('admin', __name__, url_prefix="/api/v1/admin")

@admin.post('/register_school')
def register():

   school_name = request.json['school_name']
   school_location = request.json['school_location']
   school_website = request.json['school_website']
   school_email = request.json['school_email']
   school_admin_id = request.json['school_admin_id']
   school_admin_password = request.json['school_admin_password']

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
                  }), HTTP_200_OK

@admin.post('/register_parent')
def register_parent():
   first_name = request.json['first_name']
   last_name = request.json['last_name']
   password = request.json['password']
   parent_email = request.json['parent_email']
   parent_phone = request.json['parent_phone']
   username = create_parent_username(last_name)

   if len(password) < 6:
      return jsonify({'error': 'password is too short'}), HTTP_400_BAD_REQUEST

   if not validators.email(parent_email):
      return jsonify({'error': 'Email is not valid'}), HTTP_400_BAD_REQUEST

   pwd_hash = generate_password_hash(password)

   parent = Parent(
      first_name=first_name,
      last_name=last_name,
      username = username,
      password=pwd_hash,
      parent_email=parent_email,
      parent_phone = parent_phone
   )

   db.session.add(parent)
   db.session.commit()

   return jsonify({
      'message': f'Successfully added {last_name} {first_name}',
      'parent': {
         'first_name': first_name,
         'last_name': last_name,
         'password': password,
         'parent_email': parent_email,
         'parent_phone': parent_phone,
         'username': username
      } 
         }), HTTP_200_OK
