from datetime import datetime
from src.models import db
from src.models.routes import Routes
from src.models.bus import Bus

class Trip(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   routes = db.Column(db.Integer, db.ForeignKey(Routes.id))
   date = db.Column(db.DateTime, default=datetime.now())
   start_timestamp = db.Column(db.DateTime, nullable=True,)
   end_timestamp = db.Column(db.DateTime, nullable=True)
   latest_gps = db.Column(db.Text, nullable=True)
   last_update_timestamp = db.Column(db.DateTime, nullable=True)
   bus_id = db.Column(db.Integer, db.ForeignKey(Bus.id))

   def start_timestamps(self):
      self.start_timestamp = datetime.now()
      db.session.commit()

   def end_timestamps(self):
      self.end_timestamp = datetime.now()
      db.session.commit()

   def get_latest_gps(self, gps):
      self.latest_gps = gps
      db.session.commit()
      
   def get_last_update_timestamp(self):
      self.last_update_timestamp = datetime.now()
      db.session.commit()

   def __repr__(self) -> str:
      f'Trip>>> {Trip.id}'   