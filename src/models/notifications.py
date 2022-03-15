from src.models import db
from src.models.child import Child

class Notification(db.model):
   id = db.Column(db.Integer, primary_key=True)
   message = db.Column(db.Text)
   child = db.Column(db.Integer, db.ForeignKey(Child.id))

   def __repr__(self) -> str:
      return f'message>>> {self.message}'