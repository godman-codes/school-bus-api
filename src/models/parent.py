from src.models import db

class Parent(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   first_name = db.Column(db.String(12), nullable=False)
   last_name = db.Column(db.String(12), nullable=False)
   username = db.Column(db.String(12))
   password = db.Column(db.Text, nullable=False)
   parent_email = db.Column(db.String, unique=True, nullable=False)
   parent_phone = db.Column(db.String, unique=True, nullable=False)
   child = db.relationship('Child', backref='parent')

   # def __init__(self, first_name, last_name, username,) -> None:
   #    self.first_name = first_name

   def __repr__(self) -> str:
      return f'Parent>>> {self.last_name}'