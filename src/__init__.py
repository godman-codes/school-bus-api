from flask import Flask
import os
from src.models import db
from src.auth.admin_auth import admin_auth
from src.view.admin import admin
from src.auth.parent import parent
from src.view.driver import driver
from flask_jwt_extended import JWTManager



def create_app(test_config=None):
   app = Flask(__name__, instance_relative_config=True)


   if test_config is None:
      app.config.from_mapping(
         SECRET_KEY=os.environ.get('SECRET_KEY'),
         SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
         SQLALCHEMY_TRACK_MODIFICATIONS=False
      )
   else:
      app.config.from_mapping(test_config)


   
   db.app=app
   db.init_app(app)
   JWTManager(app)
   app.register_blueprint(admin)
   app.register_blueprint(admin_auth)
   app.register_blueprint(parent)
   app.register_blueprint(driver)


   return app