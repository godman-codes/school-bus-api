from src.models import db

class Child(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   first_name = db.Column(db.String(12), nullable=False)
   last_name = db.Column(db.String(12), nullable=False)
   child_class = db.Column(db.String(12), nullable=False)
   child_parent = db.Column(db.Integer, db.ForeignKey('parent.id'))

   def __repr__(self) -> str:
      return f'Child>>> {self.first_name}'