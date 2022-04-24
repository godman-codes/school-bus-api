from src.models import db
class Routes(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   routes_path = db.Column(db.Text, unique=True, nullable=False)
   expected_time = db.Column(db.String, nullable=False)
   child_routes = db.relationship('Child', backref='routes')
   active_trips = db.relationship('ActiveTrip', backref='routes_active_trips')
   scheduled_trip = db.relationship('ScheduledTrip', backref='routes_scheduled_trip')
   

   def __repr__(self) -> str:
      return f'Routes>>> {self.id}'