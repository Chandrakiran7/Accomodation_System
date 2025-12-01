"""
Sample data script for the accommodation booking platform
Run with: python manage.py shell < populate_sample_data.py
"""
import os
import django

# 1. Point to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_platform.settings')

django.setup()

from accounts.models import User, UserProfile
from accommodations.models import Category, Amenity, Accommodation, AccommodationImage
from bookings.models import Booking, Payment
from reviews.models import Review
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, timedelta

def create_sample_data():
    print("Creating sample data...")
    
    # Create categories
    categories_data = [
        {'name': 'Apartment', 'description': 'Modern apartments in city centers', 'icon': 'fas fa-building'},
        {'name': 'House', 'description': 'Entire houses for families', 'icon': 'fas fa-home'},
        {'name': 'Villa', 'description': 'Luxury villas with amenities', 'icon': 'fas fa-crown'},
        {'name': 'Studio', 'description': 'Compact studios for solo travelers', 'icon': 'fas fa-bed'},
        {'name': 'Loft', 'description': 'Spacious lofts with modern design', 'icon': 'fas fa-warehouse'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create amenities
    amenities_data = [
        {'name': 'WiFi', 'icon': 'fas fa-wifi', 'category': 'basic'},
        {'name': 'Kitchen', 'icon': 'fas fa-utensils', 'category': 'basic'},
        {'name': 'Swimming Pool', 'icon': 'fas fa-swimming-pool', 'category': 'luxury'},
        {'name': 'Parking', 'icon': 'fas fa-car', 'category': 'basic'},
        {'name': 'Air Conditioning', 'icon': 'fas fa-snowflake', 'category': 'comfort'},
        {'name': 'TV', 'icon': 'fas fa-tv', 'category': 'entertainment'},
        {'name': 'Gym', 'icon': 'fas fa-dumbbell', 'category': 'luxury'},
        {'name': 'Balcony', 'icon': 'fas fa-tree', 'category': 'comfort'},
        {'name': 'Washing Machine', 'icon': 'fas fa-tshirt', 'category': 'basic'},
        {'name': 'Pet Friendly', 'icon': 'fas fa-paw', 'category': 'special'},
    ]
    
    amenities = []
    for amenity_data in amenities_data:
        amenity, created = Amenity.objects.get_or_create(name=amenity_data['name'], defaults=amenity_data)
        amenities.append(amenity)
        if created:
            print(f"Created amenity: {amenity.name}")
    
    # Create sample users
    users_data = [
        {
            'username': 'johnhost',
            'email': 'john.host@example.com',
            'first_name': 'John',
            'last_name': 'Host',
            'role': 'host',
            'password': 'password123'
        },
        {
            'username': 'mariahost',
            'email': 'maria.host@example.com',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'role': 'host',
            'password': 'password123'
        },
        {
            'username': 'davidguest',
            'email': 'david.guest@example.com',
            'first_name': 'David',
            'last_name': 'Johnson',
            'role': 'guest',
            'password': 'password123'
        },
        {
            'username': 'sarahguest',
            'email': 'sarah.guest@example.com',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'role': 'guest',
            'password': 'password123'
        },
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_verified': True,
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                bio=f"Hello! I'm {user.first_name}.",
                city="New York" if user.role == 'host' else "San Francisco",
                country="United States",
            )
            print(f"Created user: {user.email}")
        users.append(user)
    
    # Get hosts and guests
    hosts = [u for u in users if u.role == 'host']
    guests = [u for u in users if u.role == 'guest']
    
    # Create sample accommodations
    accommodations_data = [
        {
            'title': 'Luxury Downtown Apartment',
            'description': 'Beautiful apartment in the heart of downtown with stunning city views.',
            'category': categories[0],  # Apartment
            'property_type': 'entire_place',
            'address': '123 Main St, Apt 15A',
            'city': 'New York',
            'state': 'NY',
            'country': 'United States',
            'postal_code': '10001',
            'bedrooms': 2,
            'bathrooms': 2,
            'max_guests': 4,
            'price_per_night': Decimal('199.00'),
            'host': hosts[0],
        },
        {
            'title': 'Cozy Studio Near Central Park',
            'description': 'Perfect studio for couples visiting NYC. Walking distance to Central Park.',
            'category': categories[3],  # Studio
            'property_type': 'entire_place',
            'address': '456 Park Ave',
            'city': 'New York',
            'state': 'NY',
            'country': 'United States',
            'postal_code': '10002',
            'bedrooms': 1,
            'bathrooms': 1,
            'max_guests': 2,
            'price_per_night': Decimal('149.00'),
            'host': hosts[1],
        },
        {
            'title': 'Modern Loft in Brooklyn',
            'description': 'Spacious loft with industrial design in trendy Brooklyn neighborhood.',
            'category': categories[4],  # Loft
            'property_type': 'entire_place',
            'address': '789 Brooklyn St',
            'city': 'Brooklyn',
            'state': 'NY',
            'country': 'United States',
            'postal_code': '11201',
            'bedrooms': 1,
            'bathrooms': 1,
            'max_guests': 3,
            'price_per_night': Decimal('175.00'),
            'host': hosts[0],
        },
    ]
    
    accommodations = []
    for acc_data in accommodations_data:
        accommodation, created = Accommodation.objects.get_or_create(
            title=acc_data['title'],
            defaults={**acc_data, 'status': 'active', 'is_available': True}
        )
        
        if created:
            # Add random amenities
            selected_amenities = random.sample(amenities, k=random.randint(3, 6))
            accommodation.amenities.set(selected_amenities)
            print(f"Created accommodation: {accommodation.title}")
        
        accommodations.append(accommodation)
    
    # Create sample bookings
    if guests and accommodations:
        today = timezone.now().date()
        
        # Past booking
        past_booking = Booking.objects.create(
            guest=guests[0],
            accommodation=accommodations[0],
            check_in_date=today - timedelta(days=30),
            check_out_date=today - timedelta(days=27),
            num_guests=2,
            accommodation_cost=Decimal('597.00'),  # 3 nights * 199
            total_cost=Decimal('647.00'),  # including fees
            status='completed'
        )
        
        # Create payment for past booking
        Payment.objects.create(
            booking=past_booking,
            amount=past_booking.total_cost,
            payment_method='credit_card',
            status='completed',
            paid_at=past_booking.created_at
        )
        
        # Create review for past booking
        Review.objects.create(
            guest=past_booking.guest,
            accommodation=past_booking.accommodation,
            booking=past_booking,
            overall_rating=5,
            cleanliness_rating=5,
            communication_rating=4,
            location_rating=5,
            value_rating=4,
            title='Amazing stay!',
            comment='The apartment was exactly as described. Great location and very clean. Host was very responsive.',
            would_recommend=True
        )
        
        # Future booking
        future_booking = Booking.objects.create(
            guest=guests[1],
            accommodation=accommodations[1],
            check_in_date=today + timedelta(days=15),
            check_out_date=today + timedelta(days=18),
            num_guests=2,
            accommodation_cost=Decimal('447.00'),  # 3 nights * 149
            total_cost=Decimal('497.00'),  # including fees
            status='confirmed'
        )
        
        print(f"Created {Booking.objects.count()} sample bookings")
        print(f"Created {Review.objects.count()} sample reviews")
    
    print("Sample data creation completed!")
    
    # Print summary
    print(f"""
Summary:
- Users: {User.objects.count()}
- Categories: {Category.objects.count()}
- Amenities: {Amenity.objects.count()}
- Accommodations: {Accommodation.objects.count()}
- Bookings: {Booking.objects.count()}
- Reviews: {Review.objects.count()}

Admin credentials:
- Email: admin@bookingplatform.com
- Password: admin123

Sample host credentials:
- Email: john.host@example.com
- Password: password123

Sample guest credentials:
- Email: david.guest@example.com
- Password: password123
""")

if __name__ == '__main__':
    create_sample_data()