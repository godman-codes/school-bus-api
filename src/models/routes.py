from src.models import db

class Routes(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   routes_path = db.Column(db.Text, unique=True, nullable=False)
   expected_time = db.Column(db.String, nullable=False)
   child_for_routes = db.relationship('Child', backref='routes')
   Trips = db.relationsip('Trip', backref='routes')

   def __repr__(self) -> str:
      return f'Routes>>> {self.id}'