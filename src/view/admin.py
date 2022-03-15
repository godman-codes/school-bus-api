from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from src.models.admin import School
from src.models.parent import Parent
from src.models.child import Child
from src.models.driver import Driver
from src.models.bus import Bus
from src.models import db
from src.helper.parentHelpers import create_username, phoneNumberConverter, standard_query, standard_query_bus
from src.models.routes import Routes

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
   username = create_username(last_name, Parent)

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
   child_routes = request.json['child_routes']


   if not first_name or len(first_name) < 2:
      return jsonify({'error': 'Enter a valid First Name'}), HTTP_400_BAD_REQUEST  

   if not last_name or len(last_name) < 2:
      return jsonify({'error': 'Enter a valid Last Name'}), HTTP_400_BAD_REQUEST

   if not child_parent or len(child_parent) < 2:
      return jsonify({'error': 'Enter a valid parent username'}), HTTP_400_BAD_REQUEST
   
   if not child_routes or len(child_routes) < 1:
      return jsonify({'error': 'please enter the valid child routes'}), HTTP_400_BAD_REQUEST
   
   if not child_class or len(child_class) < 2:
      return jsonify({'error': 'Enter the valid child class'}), HTTP_400_BAD_REQUEST  
   
   parent = Parent.query.filter_by(username=child_parent).first()
   routes = Routes.query.filter_by(id=child_routes).first()

   if parent is None:
      return jsonify({'error': 'username belongs to no parent'})

   if routes is None:
      return jsonify({'error': 'Route does not exist'})
   
   child = Child.query.filter_by(child_parent=parent.id, 
                                 first_name=first_name, 
                                 last_name=last_name).first()
   if child:
      return jsonify({'error': 'child already exists'}), HTTP_400_BAD_REQUEST

   child = Child(
      first_name=first_name,
      last_name=last_name,
      child_class=child_class,
      child_parent=parent.id,
      child_routes=routes.id
   )

   
   db.session.add(child)
   db.session.commit()

   return jsonify({
      'message': 'child successfully registered',
      'child': {
         'first_name': first_name,
         'last_name': last_name,
         'child_class': child_class,
         'child_parent': f'{parent.last_name} {parent.first_name}',
         'child_route': f'Routes {routes.id}'
      }
   }), HTTP_200_OK


@admin.post('/register_driver')
def register_driver():
   first_name = request.json['first_name']
   last_name = request.json['last_name']
   driver_id = create_username(last_name, Driver)
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
      'message': 'driver successfully registered',
      'driver': {
         'first_name': first_name,
         'last_name': last_name,
         'driver_id': driver_id,
         'driver_email': driver_email,
         'driver_phone': driver_phone
         }
   }), HTTP_200_OK


@admin.post('/register_bus')
def register_bus():
   bus_name = request.json['bus_name']
   bus_id = create_username(bus_name[:2], Bus)
   plate_number = request.json['plate_number']
   capacity = request.json['capacity']
   driver = request.json['driver']

   if not bus_id or len(bus_id) < 3:
      return jsonify({'error': 'Enter a valid Bus id'}), HTTP_400_BAD_REQUEST

   if not bus_name or len(bus_name) < 2:
      return jsonify({'error': 'Enter a valid Bus Name'}), HTTP_400_BAD_REQUEST

   if not capacity or int(capacity) != capacity:
      return jsonify({'error': 'error enter a valid capacity'}), HTTP_400_BAD_REQUEST

   if len(plate_number) != 8:
      return jsonify({'error': 'enter a valid plate_number'}), HTTP_400_BAD_REQUEST

   if Bus.query.filter_by(plate_number=plate_number).first() is not None:
      return jsonify({'error': 'Plate Number already exist'}), HTTP_400_BAD_REQUEST

   if Bus.query.filter_by(bus_driver=driver).first() is not None:
      return jsonify({'error': 'Driver already assigned to another bus'}), HTTP_400_BAD_REQUEST
   
   driver = Driver.query.filter_by(driver_id=driver).first()
   
   if driver is None:
      return jsonify({'error': 'driver does not exist'}), HTTP_400_BAD_REQUEST
   print('man')

   bus = Bus(
      bus_name=bus_name,
      plate_number=plate_number,
      bus_id=bus_id,
      capacity=capacity,
      bus_driver=driver.id
   )

   db.session.add(bus)
   db.session.commit()

   return jsonify({
      'message': 'child successfully registered',
      'bus': {
         'bus_name': bus_name,
         'plate_number': plate_number,
         'bus_id': bus_id,
         'capacity': capacity,
         'driver': f'{driver.last_name} {driver.first_name}'
      }
   }), HTTP_200_OK

@admin.post('/search_parent')
def search_parent():
   parent = request.json['parent']

   if parent == '':
      return jsonify({'error': 'enter a search name pls'}), HTTP_400_BAD_REQUEST
   
   all_valid_parent = standard_query(parent, Parent)
   dict_parents = {}
   size = 0
   for parent in all_valid_parent:
      dict_parents[f'parent-{size}'] = {
         'parent_id': parent.id,
         'parent_first_name': parent.first_name,
         'parent_last_name': parent.last_name,
         'parent_email': parent.parent_email,
         'parent_username': parent.username,
         'parent_phone': parent.parent_phone,
         'children': [[x.id, x.first_name, x.last_name] for x in Child.query.filter_by(child_parent=parent.id).all()]
      }
      size =+ 1
   return jsonify({
      'message': 'search successfull',
      'parents': dict_parents
   }), HTTP_200_OK

@admin.post('/search_driver')
def search_driver():
   driver = request.json['driver']

   if driver == '':
      return jsonify({'error': 'enter a search name pls'}), HTTP_400_BAD_REQUEST

   all_valid_driver = standard_query(driver, Driver)
   dict_drivers = {}
   size = 0
   for driver in all_valid_driver:
      dict_drivers[f'driver-{size}'] = {
         'driver_id': driver.id,
         'driver_first_name': driver.first_name,
         'driver_last_name': driver.last_name,
         'driver_email': driver.driver_email,
         'driver_username_id': driver.driver_id,
         'driver_phone': driver.driver_phone,
      }
      size =+ 1
   return jsonify({
      'message': 'search successful',
      'drivers': dict_drivers
   }), HTTP_200_OK


@admin.post('/search_children')
def search_children():
   child = request.json['child_name']

   if child == '':
      return jsonify({'error': 'enter a search name'}), HTTP_400_BAD_REQUEST

   all_valid_children = standard_query(child, Child)
   dict_child = {}
   size = 0
   for child in all_valid_children:
      dict_child[f'child-{size}'] = {
         'child_id': child.id,
         'child_first_name': child.first_name,
         'child_last_name': child.last_name,
         'child_parent': [[x.id, x.first_name, x.last_name] for x in Parent.query.filter_by(id=child.child_parent).all()]
      }
   size =+ 1
   return jsonify({
      'message': 'search successful',
      'child': dict_child
   }), HTTP_200_OK

@admin.post('/search_bus')
def search_bus():
   bus = request.json['bus']

   if bus == '':
      return jsonify({'error': 'enter a search name'}), HTTP_400_BAD_REQUEST

   all_valid_bus = standard_query_bus(bus, Bus)
   dict_bus = {}

   


   size = 0
   for bus in all_valid_bus:
      dict_bus[f'bus-{size}'] = {
         'bus_id': bus.id,
         'bus_name': bus.bus_name,
         'bus_plate_number': bus.plate_number,
         'bus_capacity': bus.capacity,
         'current_location': bus.current_location,
         'initial_attendance': bus.initial_attendance,
         'bus_is_active': bus.is_active,
         'bus_driver': [[x.id, x.first_name, x.last_name] for x in Driver.query.filter_by(id=bus.bus_driver).all()]
      }
   size =+ 1

   if dict_bus == {}:
      return jsonify({'error': 'no results found'}), HTTP_404_NOT_FOUND

   return jsonify({
      'message': 'search successful',
      'buses': dict_bus
      }), HTTP_302_FOUND

@admin.post('/register_routes')
def register_routes():
   routes_path = request.json['routes_path']
   expected_time = request.json['expected_time']

   if not routes_path or len(routes_path) < 2:
      return jsonify({'error': 'Enter a valid Route'}), HTTP_400_BAD_REQUEST

   if not expected_time or len(expected_time) < 2:
      return jsonify({'error': 'Enter a valid Time'}), HTTP_400_BAD_REQUEST

   if Routes.query.filter_by(routes_path=routes_path).first() is not None:
      return jsonify({'error': 'This route already exists'}), HTTP_400_BAD_REQUEST

   routes = Routes(
      routes_path=routes_path,
      expected_time=expected_time
   )

   db.session.add(routes)
   db.session.commit()

   return jsonify({
      'message': 'Route successfully registered',
      'routes': {
         'routes_path': routes_path,
         'expected_time': expected_time
      }
   }), HTTP_200_OK
   
