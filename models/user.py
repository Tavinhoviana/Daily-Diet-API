from database import db
from flask_login import UserMixin
from datetime import datetime
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    diet = db.Column(db.String(80), nullable=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(80), nullable=False, default="user")

    meals = db.relationship('Meal', back_populates='user', cascade="all, delete-orphan")
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_on_diet = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='meals')
