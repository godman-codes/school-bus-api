from src.models import db
from src.models.routes import Routes

class Child(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   first_name = db.Column(db.String(12), nullable=False)
   last_name = db.Column(db.String(12), nullable=False)
   child_class = db.Column(db.String(12), nullable=False)
   child_parent = db.Column(db.Integer, db.ForeignKey('parent.id'))
   child_routes = db.Column(db.Integer, db.ForeignKey(Routes.id))
   notifications = db.relationship('Notification', backref='child')

   def __repr__(self) -> str:
      return f'Child>>> {self.first_name}'