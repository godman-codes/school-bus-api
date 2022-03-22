from email.policy import default
from src.models import db
from src.models.child import Child
from src.models.driver import Driver
from datetime import datetime

class Notification(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   message = db.Column(db.Text)
   time = db.Column(db.DateTime, default=datetime.now())
   child = db.Column(db.Integer, db.ForeignKey(Child.id))
   driver = db.Column(db.Integer, db.ForeignKey(Driver.id))
   parent = db.Column(db.Integer, db.ForeignKey('parent.id'))

   def __repr__(self) -> str:
      return f'message>>> {self.message}'