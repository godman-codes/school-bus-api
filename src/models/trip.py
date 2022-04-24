from datetime import datetime
from src.models import db
from src.models.routes import Routes


class ScheduledTrip(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.String)
   latest_gps = db.Column(db.Text, nullable=True)
   routes = db.Column(db.Integer, db.ForeignKey(Routes.id))
   last_update_timestamp = db.Column(db.DateTime, nullable=True)
   bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'))

   def get_latest_gps(self, gps):
      self.latest_gps = gps
      db.session.commit()
      return self.latest_gps
      
   def get_last_update_timestamp(self):
      self.last_update_timestamp = datetime.now()
      db.session.commit()
      return self.last_update_timestamp
   
   def __repr__(self) -> str:
      return f'ScheduledTrip>>> {ScheduledTrip.id}'

class ActiveTrip(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.String)
   start_timestamp = db.Column(db.DateTime, nullable=True,)
   # end_timestamp = db.Column(db.DateTime, nullable=True)
   latest_gps = db.Column(db.Text)
   last_update_timestamp = db.Column(db.DateTime, nullable=True)
   routes = db.Column(db.Integer, db.ForeignKey(Routes.id))
   bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'))
   attendance = db.relationship('Attendance', backref='active_attendance')

   def start_timestamps(self):
      self.start_timestamp = datetime.now()
      db.session.commit()
      return self.start_timestamp

   def end_timestamps(self):
      self.end_timestamp = datetime.now()
      db.session.commit()
      return self.end_timestamp

   def get_latest_gps(self, gps):
      self.latest_gps = gps
      db.session.commit()
      return self.latest_gps
      
   def get_last_update_timestamp(self):
      self.last_update_timestamp = datetime.now()
      db.session.commit()
      return self.last_update_timestamp

   def __repr__(self) -> str:
      return f'ActiveTrip>>> {ActiveTrip.id}'

   

class CompletedTrip(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.String)
   start_timestamp = db.Column(db.DateTime, nullable=False)
   end_timestamp = db.Column(db.DateTime, nullable=False)
   last_gps = db.Column(db.Text, nullable=True)
   last_update_timestamp = db.Column(db.DateTime, nullable=True)
   routes = db.Column(db.Integer, nullable=False)
   bus_id = db.Column(db.Integer, nullable=False)
   attendance = db.Column(db.Text)

   # def end_timestamps(self):
   #    self.end_timestamp = datetime.now()
   #    db.session.commit()
   #    return self.end_timestamp

   def __repr__(self) -> str:
      return f'CompletedTrip>>> {CompletedTrip.id}'

