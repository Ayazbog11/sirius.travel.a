from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Класс Place — модель для хранения информации о местах
class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(120), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    reviews = db.relationship('Review', backref='place', lazy=True)

    #средняя оценка по отзывам
    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

# Класс Review — модель для хранения отзывов к месту
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)  # ссылка на Place (ID места)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
