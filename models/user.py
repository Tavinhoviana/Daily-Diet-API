from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    # id (int), username (txt), description (txt), date and time, (int), diet (txt)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=False)
    description = db.Column(db.String(500),nullable=False, unique=False)
    datetime = db.Column(db.Integer, nullable=False, unique=False)
    diet = db.Column(db.String(80),nullable=False, unique=False)