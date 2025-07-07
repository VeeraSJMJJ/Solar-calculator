from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    tariff = db.Column(db.Float)
    units = db.Column(db.Float)
    billing_cycle = db.Column(db.String(20))
    total_savings = db.Column(db.Float)
