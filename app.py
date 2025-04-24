from flask import Flask, request, jsonify
from datetime import datetime
from models import Event, TicketCategory, Booking
from database import db
import pytz
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()

    required_fields = ["name", "venue", "date", "ticket_categories", "details"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Enhanced date parsing and validation
        event_date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
        now = datetime.now(pytz.UTC)

        # Check if date is in future (with 1-hour buffer)
        if event_date <= now.replace(tzinfo=pytz.UTC):
            return jsonify({"error": "Event date must be in the future"}), 400

        # Ensure date is within reasonable range (e.g., not more than 2 years in future)
        if event_date > now.replace(tzinfo=pytz.UTC).replace(year=now.year + 2):
            return jsonify({"error": "Event date too far in future"}), 400

    except ValueError:
        return jsonify({"error": "Invalid date format."}), 400

    event = Event(
        name=data["name"], venue=data["venue"], date=event_date, details=data["details"]
    )

    for category in data["ticket_categories"]:
        required_category_fields = ["name", "price", "seats_limit"]
        if not all(key in category for key in required_category_fields):
            return jsonify({"error": "Invalid ticket category data"}), 400

        if category["price"] < 0 or category["seats_limit"] < 0:
            return jsonify({"error": "Price and seats limit must be non-negative"}), 400

        ticket_category = TicketCategory(
            name=category["name"],
            price=category["price"],
            seats_limit=category["seats_limit"],
            seats_sold=0,
            event=event,
        )
        db.session.add(ticket_category)

    db.session.add(event)
    try:
        db.session.commit()
        return jsonify(
            {"message": "Event created successfully", "event_id": event.id}
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create event: {str(e)}"}), 500


@app.route("/events", methods=["GET"])
def list_events():
    now = datetime.now(pytz.UTC)
    events = Event.query.filter(Event.date > now).all()

    events_data = []
    for event in events:
        ticket_categories = [
            {
                "name": tc.name,
                "price": tc.price,
                "seats_limit": tc.seats_limit,
                "seats_sold": tc.seats_sold,
                "seats_available": tc.seats_limit - tc.seats_sold,
            }
            for tc in event.ticket_categories
        ]

        events_data.append(
            {
                "id": event.id,
                "name": event.name,
                "venue": event.venue,
                "date": event.date.isoformat(),
                "details": event.details,
                "ticket_categories": ticket_categories,
            }
        )

    return jsonify(events_data), 200


@app.route("/events/<int:event_id>/book", methods=["POST"])
def book_tickets(event_id):
    data = request.get_json()

    required_fields = ["ticket_category", "quantity", "user_id"]
    if not all(key in data for key in required_fields):
        return jsonify(
            {"error": "Missing required fields (ticket_category, quantity, user_id)"}
        ), 400

    if not isinstance(data["quantity"], int) or data["quantity"] <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if event.date < datetime.now(pytz.UTC):
        return jsonify({"error": "Cannot book tickets for past events"}), 400

    ticket_category = None
    for tc in event.ticket_categories:
        if tc.name == data["ticket_category"]:
            ticket_category = tc
            break

    if not ticket_category:
        return jsonify({"error": "Ticket category not found"}), 404

    available_seats = ticket_category.seats_limit - ticket_category.seats_sold
    if data["quantity"] > available_seats:
        return jsonify({"error": f"Only {available_seats} seats available"}), 400

    # Check for duplicate booking
    existing_booking = Booking.query.filter_by(
        event_id=event_id,
        user_id=data["user_id"],
        ticket_category_id=ticket_category.id,
    ).first()

    if existing_booking:
        return jsonify(
            {"error": "User has already booked tickets for this event and category"}
        ), 400

    # Create new booking
    booking_id = str(uuid.uuid4())
    booking = Booking(
        booking_id=booking_id,
        event_id=event_id,
        ticket_category_id=ticket_category.id,
        user_id=data["user_id"],
        quantity=data["quantity"],
        booking_time=datetime.now(pytz.UTC),
    )

    ticket_category.seats_sold += data["quantity"]

    try:
        db.session.add(booking)
        db.session.commit()
        return jsonify(
            {
                "message": "Tickets booked successfully",
                "booking_id": booking_id,
                "event_id": event.id,
                "ticket_category": ticket_category.name,
                "quantity": data["quantity"],
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to book tickets: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
