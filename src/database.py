from enum import unique
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class School(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   school_name = db.Column(db.String(80), unique=True, nullable=False)
   school_location = db.Column(db.String, unique=True, nullable=False)
   school_website = db.Column(db.String, unique=True, nullable=False)
   school_email = db.Column(db.String, unique=True, nullable=False)
   school_admin_id = db.Column(db.String(10), unique=True, nullable=False)
   school_admin_password = db.Column(db.Text, nullable=False)
   account_created_at = db.Column(db.DateTime, default=datetime.now())


   def __repr__(self) -> str:
      return f'School>>> {self.school_name}'