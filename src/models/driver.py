from src.models import db
from src.models.bus import Bus
class Driver(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   first_name = db.Column(db.String(12), nullable=False)
   last_name = db.Column(db.String(12), nullable=False)
   driver_id = db.Column(db.String(12))
   password = db.Column(db.Text, nullable=False)
   driver_email = db.Column(db.String, unique=True, nullable=False)
   driver_phone = db.Column(db.String, unique=True, nullable=False)
   bus = db.relationship(Bus, backref='driver_bus')
   notification = db.relationship('Notification', backref='')

   def __repr__(self) -> str:
      return f'Driver>>> {self.last_name}'