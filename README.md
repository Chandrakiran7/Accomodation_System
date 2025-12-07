# Accommodation Booking Platform

A Django-based web application for booking accommodations, similar to Airbnb.

## Features

### CRUD Operations
- **Create**: Register users, add accommodations, create bookings, add reviews
- **Read**: View accommodations, bookings, user profiles, reviews
- **Update**: Edit profiles, update accommodations, modify bookings
- **Delete**: Remove accounts, listings, bookings, reviews

### Non-CRUD Operations
- User authentication and authorization
- Role-based access control (admin, host, guest)
- Search and filtering accommodations
- Payment processing (Stripe integration)
- Notifications system
- Security features
- CI/CD pipeline ready

## Setup Instructions

### Prerequisites
- Python 3.8+
- VSCode with Python extension

### Installation
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create `.env` file with your environment variables
6. Run migrations:
   ```bash
   python manage.py migrate
   ```
7. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
8. Run development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure
```
bookin
g_platform/
├── booking_platform/          # Main project settings
├── venv/                      # Virtual environment
├── static/                    # Static files
├── media/                     # Media files
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── manage.py                  # Django management script
```

## Database
- **Development**: SQLite (db.sqlite3)
- **Production**: PostgreSQL (AWS RDS)

## Deployment
- **Platform**: AWS
- **Services**: EC2, RDS, S3, CloudFront



#Data
#Host
username: mariahost
email': maria.host@example.com
password :password123

#Data 
Guest
username: davidguest
email: david.guest@example.com
password :password123

## License
MIT License
