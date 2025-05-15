from database import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    # id (int), username (txt), description (txt), date and time, (DT), diet (txt)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500),nullable=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    diet = db.Column(db.String(80),nullable=True)