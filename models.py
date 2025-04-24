from database import db
from datetime import datetime


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.Text, nullable=False)
    ticket_categories = db.relationship("TicketCategory", backref="event", lazy=True)


class TicketCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_limit = db.Column(db.Integer, nullable=False)
    seats_sold = db.Column(db.Integer, nullable=False, default=0)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(36), unique=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    ticket_category_id = db.Column(
        db.Integer, db.ForeignKey("ticket_category.id"), nullable=False
    )
    user_id = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)

    event = db.relationship("Event", backref="bookings")
    ticket_category = db.relationship("TicketCategory", backref="bookings")
