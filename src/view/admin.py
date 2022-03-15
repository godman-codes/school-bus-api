from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from src.models.admin import School
from src.models.parent import Parent
from src.models.child import Child
from src.models.driver import Driver
from src.models import db
from src.helper.parentHelpers import create_username, phoneNumberConverter, standard_query

admin = Blueprint('admin', __name__, url_prefix="/api/v1/admin")

@admin.post('/register_school')
def register():

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
                  }), HTTP_200_OK

@admin.post('/register_parent')
def register_parent():
   first_name = request.json['first_name']
   last_name = request.json['last_name']
   password = request.json['password']
   parent_email = request.json['parent_email']
   parent_phone = request.json['parent_phone']
   username = create_username(last_name)

   if not first_name or len(first_name) < 2:
      return jsonify({'error': 'Enter a valid First Name'}), HTTP_400_BAD_REQUEST      

   if not last_name or len(last_name) < 2:
      return jsonify({'error': 'Enter a valid Last Name'}), HTTP_400_BAD_REQUEST

   if len(password) < 6:
      return jsonify({'error': 'password is too short'}), HTTP_400_BAD_REQUEST

   if not validators.email(parent_email):
      return jsonify({'error': 'Email is not valid'}), HTTP_400_BAD_REQUEST

   if not parent_phone:
      return jsonify({'error': 'Enter a valid Phone Number'}), HTTP_400_BAD_REQUEST

   if len(parent_phone) not in [11, 14] :
      return jsonify({'error': 'Enter a valid Phone Number'}), HTTP_400_BAD_REQUEST

   

   if len(parent_phone) == 11:
      parent_phone=phoneNumberConverter(parent_phone)
      if Parent.query.filter_by(parent_phone=parent_phone).first() is not None:
         return jsonify({'error': 'This phone number already exists'}), HTTP_400_BAD_REQUEST

   else:
      if Parent.query.filter_by(parent_phone=parent_phone).first() is not None:
         return jsonify({'error': 'This phone number already exists'}), HTTP_400_BAD_REQUEST


   if Parent.query.filter_by(parent_email=parent_email).first() is not None:
      return jsonify({'error': 'Email already exists'})

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

@admin.post('/register_child')
def register_child():
   first_name = request.json['first_name']
   last_name = request.json['last_name']
   child_class = request.json['child_class']
   child_parent = request.json['child_parent']


   if not first_name or len(first_name) < 2:
      return jsonify({'error': 'Enter a valid First Name'}), HTTP_400_BAD_REQUEST  

   if not last_name or len(last_name) < 2:
      return jsonify({'error': 'Enter a valid Last Name'}), HTTP_400_BAD_REQUEST

   if not child_parent or len(child_parent) < 2:
      return jsonify({'error': 'Enter a valid parent username'}), HTTP_400_BAD_REQUEST
   
   if not child_class or len(child_class) < 2:
      return jsonify({'error': 'Enter the valid child class'}), HTTP_400_BAD_REQUEST  
   
   parent = Parent.query.filter_by(username=child_parent).first()

   if parent is None:
      return jsonify({'error': 'username belongs to no parent'})
   
   child = Child.query.filter_by(child_parent=parent.id, 
                                 first_name=first_name, 
                                 last_name=last_name).first()
   if child:
      return jsonify({'error': 'child already exists'}), HTTP_400_BAD_REQUEST

   child = Child(
      first_name=first_name,
      last_name=last_name,
      child_class=child_class,
      child_parent=parent.id
   )

   
   db.session.add(child)
   db.session.commit()

   return jsonify({
      'message': 'child succesfully registered',
      'child': {
         'first_name': first_name,
         'last_name': last_name,
         'child_class': child_class,
         'child_parent': f'{parent.last_name} {parent.first_name}'
      }
   }), HTTP_200_OK


@admin.post('/register_driver')
def register_driver():
   first_name = request.json['first_name']
   last_name = request.json['last_name']
   driver_id = create_username(last_name)
   password = request.json['password']
   driver_email = request.json['driver_email']
   driver_phone = request.json['driver_phone']

   driver = Driver.query.filter_by( 
                                 first_name=first_name, 
                                 last_name=last_name,
                                 driver_phone=driver_phone).first()
   if driver:
      return jsonify({'error': 'driver already exists'}), HTTP_400_BAD_REQUEST
   
   if not first_name or len(first_name) < 2:
      return jsonify({'error': 'Enter a valid First Name'}), HTTP_400_BAD_REQUEST      

   if not last_name or len(last_name) < 2:
      return jsonify({'error': 'Enter a valid Last Name'}), HTTP_400_BAD_REQUEST

   if not driver_phone or len(driver_phone) not in [11, 14]:
      return jsonify({'error': 'Enter a valid Phone Number'}), HTTP_400_BAD_REQUEST

   if len(driver_phone) == 11:
      driver_phone=phoneNumberConverter(driver_phone)
      if Driver.query.filter_by(driver_phone=driver_phone).first() is not None:
         return jsonify({'error': 'This phone number already exists'}), HTTP_400_BAD_REQUEST

   else:
      if Driver.query.filter_by(driver_phone=driver_phone).first() is not None:
         return jsonify({'error': 'This phone number already exists'}), HTTP_400_BAD_REQUEST

   if len(password) < 6:
      return jsonify({'error': 'password is too short'}), HTTP_400_BAD_REQUEST

   if not validators.email(driver_email):
      return jsonify({'error': 'Email is not valid'}), HTTP_400_BAD_REQUEST


   pwd_hash = generate_password_hash(password)

   driver = Driver(
      first_name=first_name,
      last_name=last_name,
      driver_id=driver_id,
      password=pwd_hash,
      driver_email=driver_email,
      driver_phone=driver_phone
   )

   db.session.add(driver)
   db.session.commit()

   return jsonify({
      'message': 'driver succesfully registered',
      'driver': {
         'first_name': first_name,
         'last_name': last_name,
         'driver_id': driver_id,
         'driver_email': driver_email,
         'driver_phone': driver_phone
         }
   }), HTTP_200_OK

@admin.post('/search_parent')
def search_parent():
   parent = request.json['parent']

   if parent == '':
      return jsonify({'error': 'enter a parents name pls'})
   
   all_valid_parent = standard_query(parent, Parent)
   dict_parents = {}
   for parent in all_valid_parent:
      i = 0
      dict_parents[f'parent-{i}'] = {
         'parent_id': parent.id,
         'parent_first_name': parent.first_name,
         'parent_last_name': parent.last_name,
         'parent_email': parent.parent_email,
         'parent_username': parent.username,
         'parent_phone': parent.parent_phone,
         'children': [[x.id, x.first_name, x.last_name] for x in Child.query.filter_by(child_parent=parent.id).all()]
      }
   return jsonify({
      'message': 'search successfull',
      'parents': dict_parents
   }), HTTP_200_OK
   
   