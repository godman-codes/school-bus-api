from flask import Flask
import os


def create_app(test_config=None):
   app = Flask(__name__, instance_relative_config=True)

   if test_config is None:
      app.config.from_mapping(
         SERET_KEY=os.environ.get('SECRET_KEY'),
         SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
         SQLALCHEMY_TRACK_MODIFICATIONS=False
      )
   else:
      app.config.from_mapping(test_config)

   return app