from datetime import timedelta
from flask import Flask, jsonify
import os
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.models import db
from src.auth.admin_auth import admin_auth
from src.view.admin import admin
from src.auth.parent import parent
from src.view.driver import driver
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from src.configur.swagger import template, swagger_config
from flask_cors import CORS


def create_app(test_config=None):
   app = Flask(__name__, instance_relative_config=True)


   if test_config is None:
      app.config.from_mapping(
         SECRET_KEY=os.environ.get('SECRET_KEY'),
         SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
         SQLALCHEMY_TRACK_MODIFICATIONS=False,
         JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
         JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=5),

         SWAGGER={
            "title": "School Bus API",
            "uiversion": 3
         }
      )
   else:
      app.config.from_mapping(
         SECRET_KEY=os.environ.get('SECRET_KEY'),
         SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
         TESTING=True
      )


   
   CORS(app, supports_credentials=True)
   db.app=app
   db.init_app(app)
   JWTManager(app)
   app.register_blueprint(admin)
   app.register_blueprint(admin_auth)
   app.register_blueprint(parent)
   app.register_blueprint(driver)

   Swagger(app, config=swagger_config, template=template)

   @app.errorhandler(HTTP_404_NOT_FOUND)
   def handle_404(e):
      return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

   @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
   def handle_500(e):
      return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

   return app