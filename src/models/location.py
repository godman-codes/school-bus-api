from src.models import db
from datetime import datetime
# from src.models.trip import ActiveTrip, CompletedTrip, ScheduledTrip

class Location(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   gps = db.Column(db.Text)
   times_stamp = db.Column(db.DateTime)
   trip_id = db.Column(db.Integer)
   # Scheduled_trip_id = db.Column(db.Integer, db.ForeignKey(ScheduledTrip.id))
   # completed_trip_id = db.Column(db.Integer, db.ForeignKey(CompletedTrip.id))

   def get_times_stamp(self):
      self.times_stamp = datetime.now()
      db.session.commit()

   def update_location(self, gps):
      self.gps = gps
      db.session.commit()

   def __repr__(self) -> str:
      return f'Location of trip {self.trip_id}'