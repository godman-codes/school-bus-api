import datetime
from src.models import db
from src.models.child import Child
from datetime import datetime

class Attendance(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   is_pick_present = db.Column(db.Boolean, default=False)
   is_drop_present = db.Column(db.Boolean, default=False)
   pick_gps = db.Column(db.Text)
   drop_gps = db.Column(db.Text)
   pick_time = db.Column(db.DateTime)
   drop_time = db.Column(db.DateTime)
   child_id = db.Column(db.Integer, db.ForeignKey(Child.id))

   def picked(self, gps):
      self.is_pick_present = True
      self.pick_time = datetime.now()
      self.pick_gps = gps
      db.session.commit()

   def dropped(self, gps):
      self.is_drop_present = True
      self.drop_time = datetime.now()
      self.drop_gps = gps
      db.session.commit()

   def __repr__(self) -> str:
      return f'Attendance of {child_id}'