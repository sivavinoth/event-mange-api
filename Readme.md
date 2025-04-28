# Event Booking System API

A Flask-based REST API for managing events and ticket bookings. This system allows organizers to create events with multiple ticket categories and enables users to book tickets for available events.

## Features

- Create and manage events with venue, date and details
- Support for multiple ticket categories with different pricing
- Real-time seat availability tracking
- Prevent duplicate bookings
- Input validation and error handling
- Future date validation for events

## API Endpoints

- `POST /events` - Create a new event
- `GET /events` - List all upcoming events
- `POST /events/<event_id>/book` - Book tickets for an event

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize database: `flask db upgrade`
4. Run the application: `python app.py`

## Technologies Used

- Flask
- SQLAlchemy
- SQLite
- Python UUID
- PyTZ

## Demo Video



Note: To add your video:
1. Record a demonstration of the API
2. Upload the video file to your preferred platform (YouTube, Vimeo, etc.)
3. Replace the placeholder text above with your video link

Event-Mange-ApiTest.mp4