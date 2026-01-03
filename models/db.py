# models/db.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='generated')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)