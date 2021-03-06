from src.models import db
from src.models.trip import ScheduledTrip, ActiveTrip
class Bus(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   bus_name = db.Column(db.String, nullable=False)
   plate_number = db.Column(db.String, unique=True, nullable=False)
   bus_id = db.Column(db.String, nullable=False, unique=True)
   capacity = db.Column(db.Integer, nullable=False)
   initial_attendance = db.Column(db.Integer, default=0)
   is_active = db.Column(db.Boolean, default=False)
   bus_driver = db.Column(db.Integer, db.ForeignKey('driver.id'))
   scheduled_trip = db.relationship(ScheduledTrip, backref='bus_scheduled_trip')
   active_trip = db.relationship(ActiveTrip, backref='bus_active_trip')


   def activate_bus(self):
      self.is_active = True
      db.session.commit()
      return self.is_active

   def deactivate_bus(self):
      self.is_active = False
      db.session.commit()
      return self.is_active
      
   def __repr__(self) -> str:
      return f'Bus>> {self.bus_id}'