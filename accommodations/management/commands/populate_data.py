"""
FIXED Database Population Management Command
File: accommodations/management/commands/populate_data.py

This fixes the UNIQUE constraint error by ensuring:
- Only one review per guest-accommodation combination
- Proper matching of guests with different accommodations
- Better error handling and transaction management
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from accounts.models import User, UserProfile
from accommodations.models import Category, Amenity, Accommodation, AccommodationImage
from bookings.models import Booking
from reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data (FIXED VERSION)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        try:
            with transaction.atomic():
                # Clear existing data
                self.clear_existing_data()
                
                # Create sample data
                self.create_categories()
                self.create_amenities()
                self.create_users()
                self.create_accommodations()
                self.create_bookings()
                self.create_reviews()
                
            self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
            self.display_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during population: {str(e)}')
            )
            raise

    def clear_existing_data(self):
        """Clear all existing data"""
        self.stdout.write('Clearing existing data...')
        
        # Delete in proper order to avoid foreign key constraints
        Review.objects.all().delete()
        Booking.objects.all().delete()
        AccommodationImage.objects.all().delete()
        Accommodation.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Amenity.objects.all().delete()
        Category.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✓ Cleared existing data'))

    def create_categories(self):
        """Create property categories"""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            {'name': 'Apartment', 'description': 'Modern apartments in city centers', 'icon': 'fas fa-building'},
            {'name': 'House', 'description': 'Entire houses for families and groups', 'icon': 'fas fa-home'},
            {'name': 'Villa', 'description': 'Luxury villas with premium amenities', 'icon': 'fas fa-crown'},
            {'name': 'Studio', 'description': 'Compact studios perfect for solo travelers', 'icon': 'fas fa-bed'},
            {'name': 'Cottage', 'description': 'Charming cottages in countryside', 'icon': 'fas fa-tree'},
            {'name': 'Loft', 'description': 'Stylish lofts with unique designs', 'icon': 'fas fa-warehouse'},
            {'name': 'Penthouse', 'description': 'Exclusive penthouses with city views', 'icon': 'fas fa-city'},
            {'name': 'Cabin', 'description': 'Cozy cabins in natural settings', 'icon': 'fas fa-mountain'},
        ]
        
        for cat_data in categories_data:
            Category.objects.create(**cat_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories_data)} categories'))

    def create_amenities(self):
        """Create amenities"""
        self.stdout.write('Creating amenities...')
        
        amenities_data = [
            {'name': 'WiFi', 'icon': 'fas fa-wifi', 'category': 'basic'},
            {'name': 'Kitchen', 'icon': 'fas fa-utensils', 'category': 'basic'},
            {'name': 'Washing Machine', 'icon': 'fas fa-tshirt', 'category': 'basic'},
            {'name': 'Air Conditioning', 'icon': 'fas fa-snowflake', 'category': 'comfort'},
            {'name': 'Heating', 'icon': 'fas fa-fire', 'category': 'comfort'},
            {'name': 'TV', 'icon': 'fas fa-tv', 'category': 'entertainment'},
            {'name': 'Netflix', 'icon': 'fab fa-youtube', 'category': 'entertainment'},
            {'name': 'Swimming Pool', 'icon': 'fas fa-swimming-pool', 'category': 'luxury'},
            {'name': 'Hot Tub', 'icon': 'fas fa-hot-tub', 'category': 'luxury'},
            {'name': 'Gym', 'icon': 'fas fa-dumbbell', 'category': 'fitness'},
            {'name': 'Parking', 'icon': 'fas fa-parking', 'category': 'practical'},
            {'name': 'Pet Friendly', 'icon': 'fas fa-paw', 'category': 'practical'},
            {'name': 'Balcony', 'icon': 'fas fa-building', 'category': 'comfort'},
            {'name': 'Garden', 'icon': 'fas fa-leaf', 'category': 'outdoor'},
            {'name': 'BBQ Grill', 'icon': 'fas fa-fire-burner', 'category': 'outdoor'},
            {'name': 'Fireplace', 'icon': 'fas fa-fire', 'category': 'comfort'},
            {'name': 'Workspace', 'icon': 'fas fa-laptop', 'category': 'business'},
            {'name': 'Elevator', 'icon': 'fas fa-elevator', 'category': 'practical'},
            {'name': 'Doorman', 'icon': 'fas fa-concierge-bell', 'category': 'luxury'},
            {'name': 'Beach Access', 'icon': 'fas fa-umbrella-beach', 'category': 'location'},
        ]
        
        for amenity_data in amenities_data:
            Amenity.objects.create(**amenity_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(amenities_data)} amenities'))

    def create_users(self):
        """Create sample users"""
        self.stdout.write('Creating users...')
        
        # Create superuser
        admin = User.objects.create_user(
            username='admin',
            email='admin@bookingplatform.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_superuser=True,
            is_staff=True
        )
        UserProfile.objects.create(
            user=admin,
            bio='Platform administrator with full access to all features.',
            city='San Francisco',
            country='United States'
        )
        
        # Create hosts
        hosts_data = [
            {
                'username': 'john_host', 'email': 'john.host@example.com',
                'first_name': 'John', 'last_name': 'Smith',
                'phone': '+1-555-0101',
                'bio': 'Experienced host with 5+ years in hospitality. I love meeting people from around the world!',
                'city': 'New York', 'country': 'United States'
            },
            {
                'username': 'maria_host', 'email': 'maria.garcia@example.com',
                'first_name': 'Maria', 'last_name': 'Garcia',
                'phone': '+1-555-0102',
                'bio': 'Professional interior designer turned Airbnb host. I ensure every property is beautifully designed.',
                'city': 'Los Angeles', 'country': 'United States'
            },
            {
                'username': 'david_host', 'email': 'david.wilson@example.com',
                'first_name': 'David', 'last_name': 'Wilson',
                'phone': '+1-555-0103',
                'bio': 'Real estate investor with luxury properties in prime locations. Quality and comfort guaranteed!',
                'city': 'Miami', 'country': 'United States'
            },
            {
                'username': 'sarah_host', 'email': 'sarah.johnson@example.com',
                'first_name': 'Sarah', 'last_name': 'Johnson',
                'phone': '+1-555-0104',
                'bio': 'Family-friendly host with kid-safe properties. Perfect for family vacations and business trips.',
                'city': 'Chicago', 'country': 'United States'
            },
            {
                'username': 'alex_host', 'email': 'alex.chen@example.com',
                'first_name': 'Alex', 'last_name': 'Chen',
                'phone': '+1-555-0105',
                'bio': 'Tech entrepreneur offering modern, smart-home equipped properties with high-speed internet.',
                'city': 'San Francisco', 'country': 'United States'
            }
        ]
        
        self.hosts = []
        for host_data in hosts_data:
            bio = host_data.pop('bio')
            city = host_data.pop('city')
            country = host_data.pop('country')
            
            user = User.objects.create_user(
                password='password123',
                role='host',
                **host_data
            )
            UserProfile.objects.create(user=user, bio=bio, city=city, country=country)
            self.hosts.append(user)
        
        # Create guests
        guests_data = [
            {
                'username': 'guest1', 'email': 'david.guest@example.com',
                'first_name': 'David', 'last_name': 'Miller',
                'phone': '+1-555-0201',
                'bio': 'Digital nomad exploring the world one city at a time.',
                'city': 'Austin', 'country': 'United States'
            },
            {
                'username': 'guest2', 'email': 'emma.travel@example.com',
                'first_name': 'Emma', 'last_name': 'Thompson',
                'phone': '+1-555-0202',
                'bio': 'Travel blogger sharing amazing accommodation experiences.',
                'city': 'Portland', 'country': 'United States'
            },
            {
                'username': 'guest3', 'email': 'mike.business@example.com',
                'first_name': 'Michael', 'last_name': 'Brown',
                'phone': '+1-555-0203',
                'bio': 'Business traveler looking for comfortable, well-located stays.',
                'city': 'Boston', 'country': 'United States'
            },
            {
                'username': 'guest4', 'email': 'lisa.family@example.com',
                'first_name': 'Lisa', 'last_name': 'Anderson',
                'phone': '+1-555-0204',
                'bio': 'Family vacation planner seeking kid-friendly accommodations.',
                'city': 'Seattle', 'country': 'United States'
            },
            {
                'username': 'guest5', 'email': 'robert.solo@example.com',
                'first_name': 'Robert', 'last_name': 'Taylor',
                'phone': '+1-555-0205',
                'bio': 'Solo traveler who appreciates unique and authentic experiences.',
                'city': 'Denver', 'country': 'United States'
            },
            {
                'username': 'guest6', 'email': 'jennifer.couple@example.com',
                'first_name': 'Jennifer', 'last_name': 'Lee',
                'phone': '+1-555-0206',
                'bio': 'Traveling with my partner, looking for romantic getaways and city adventures.',
                'city': 'Las Vegas', 'country': 'United States'
            }
        ]
        
        self.guests = []
        for guest_data in guests_data:
            bio = guest_data.pop('bio')
            city = guest_data.pop('city')
            country = guest_data.pop('country')
            
            user = User.objects.create_user(
                password='password123',
                role='guest',
                **guest_data
            )
            UserProfile.objects.create(user=user, bio=bio, city=city, country=country)
            self.guests.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created 1 admin, {len(hosts_data)} hosts, {len(guests_data)} guests'))

    def create_accommodations(self):
        """Create sample accommodations"""
        self.stdout.write('Creating accommodations...')
        
        categories = list(Category.objects.all())
        amenities = list(Amenity.objects.all())
        
        accommodations_data = [
            {
                'host': self.hosts[0],
                'title': 'Luxury Downtown Apartment with City Views',
                'description': 'Experience the best of city living in this stunning 2-bedroom apartment located in the heart of downtown. Floor-to-ceiling windows offer breathtaking city skyline views, while the modern kitchen and spacious living area provide the perfect space for both relaxation and entertainment.',
                'category': categories[0],
                'property_type': 'entire_place',
                'address': '123 Main Street, Suite 1505',
                'city': 'New York',
                'state': 'New York',
                'country': 'United States',
                'postal_code': '10001',
                'bedrooms': 2,
                'bathrooms': 2,
                'max_guests': 4,
                'area_sqft': 1200,
                'price_per_night': Decimal('180.00'),
                'cleaning_fee': Decimal('50.00'),
                'security_deposit': Decimal('200.00'),
                'min_nights': 2,
                'max_nights': 30,
                'amenity_indices': [0, 1, 2, 3, 5, 6, 10, 12, 16, 17]
            },
            {
                'host': self.hosts[1],
                'title': 'Charming Victorian House Near Beach',
                'description': 'Step back in time in this beautifully restored Victorian house just 3 blocks from the beach. Original hardwood floors, vintage fixtures, and modern amenities create the perfect blend of historic charm and contemporary comfort.',
                'category': categories[1],
                'property_type': 'entire_place',
                'address': '456 Ocean Avenue',
                'city': 'Santa Monica',
                'state': 'California',
                'country': 'United States',
                'postal_code': '90401',
                'bedrooms': 3,
                'bathrooms': 2,
                'max_guests': 6,
                'area_sqft': 1800,
                'price_per_night': Decimal('250.00'),
                'cleaning_fee': Decimal('75.00'),
                'security_deposit': Decimal('300.00'),
                'min_nights': 3,
                'max_nights': 14,
                'amenity_indices': [0, 1, 2, 4, 5, 10, 11, 13, 14, 15, 19]
            },
            {
                'host': self.hosts[2],
                'title': 'Modern Villa with Private Pool & Mountain Views',
                'description': 'Escape to luxury in this contemporary villa featuring panoramic mountain views and a private infinity pool. The open-concept design seamlessly blends indoor and outdoor living, with a gourmet kitchen and spa-like bathrooms.',
                'category': categories[2],
                'property_type': 'entire_place',
                'address': '789 Hillside Drive',
                'city': 'Scottsdale',
                'state': 'Arizona',
                'country': 'United States',
                'postal_code': '85255',
                'bedrooms': 4,
                'bathrooms': 3,
                'max_guests': 8,
                'area_sqft': 3200,
                'price_per_night': Decimal('450.00'),
                'cleaning_fee': Decimal('100.00'),
                'security_deposit': Decimal('500.00'),
                'min_nights': 3,
                'max_nights': 21,
                'amenity_indices': [0, 1, 2, 3, 5, 7, 8, 9, 10, 13, 14, 16, 18]
            },
            {
                'host': self.hosts[0],
                'title': 'Cozy Studio in Arts District',
                'description': 'Perfect for solo travelers or couples, this stylish studio in the vibrant Arts District combines comfort with creativity. Exposed brick walls, high ceilings, and carefully curated local artwork create an inspiring atmosphere.',
                'category': categories[3],
                'property_type': 'entire_place',
                'address': '321 Gallery Street, Unit 4B',
                'city': 'Chicago',
                'state': 'Illinois',
                'country': 'United States',
                'postal_code': '60614',
                'bedrooms': 1,
                'bathrooms': 1,
                'max_guests': 2,
                'area_sqft': 650,
                'price_per_night': Decimal('95.00'),
                'cleaning_fee': Decimal('30.00'),
                'security_deposit': Decimal('100.00'),
                'min_nights': 1,
                'max_nights': 14,
                'amenity_indices': [0, 1, 2, 3, 5, 16, 17]
            },
            {
                'host': self.hosts[3],
                'title': 'Family-Friendly Cottage with Large Yard',
                'description': 'Create lasting family memories in this spacious cottage featuring a large fenced yard, playground, and game room. The fully equipped kitchen makes family meals easy, while the cozy living room provides the perfect gathering space.',
                'category': categories[4],
                'property_type': 'entire_place',
                'address': '654 Maple Lane',
                'city': 'Portland',
                'state': 'Oregon',
                'country': 'United States',
                'postal_code': '97205',
                'bedrooms': 3,
                'bathrooms': 2,
                'max_guests': 6,
                'area_sqft': 1600,
                'price_per_night': Decimal('160.00'),
                'cleaning_fee': Decimal('60.00'),
                'security_deposit': Decimal('250.00'),
                'min_nights': 2,
                'max_nights': 14,
                'amenity_indices': [0, 1, 2, 4, 5, 10, 11, 13, 14, 15]
            },
            {
                'host': self.hosts[4],
                'title': 'Industrial Loft with Smart Home Features',
                'description': 'Experience the future in this converted warehouse loft featuring smart home automation, industrial design elements, and cutting-edge technology. Voice-controlled lighting, temperature, and entertainment systems.',
                'category': categories[5],
                'property_type': 'entire_place',
                'address': '987 Industrial Boulevard, Loft 12',
                'city': 'Austin',
                'state': 'Texas',
                'country': 'United States',
                'postal_code': '78701',
                'bedrooms': 2,
                'bathrooms': 2,
                'max_guests': 4,
                'area_sqft': 1400,
                'price_per_night': Decimal('200.00'),
                'cleaning_fee': Decimal('55.00'),
                'security_deposit': Decimal('200.00'),
                'min_nights': 2,
                'max_nights': 30,
                'amenity_indices': [0, 1, 2, 3, 5, 6, 9, 10, 16, 17]
            },
            {
                'host': self.hosts[1],
                'title': 'Penthouse Suite with Panoramic City Views',
                'description': 'Indulge in luxury at this stunning penthouse offering 360-degree city views from the 40th floor. Floor-to-ceiling windows, a private rooftop terrace, and premium finishes throughout create an unforgettable urban retreat.',
                'category': categories[6],
                'property_type': 'entire_place',
                'address': '555 Skyline Avenue, Penthouse',
                'city': 'Miami',
                'state': 'Florida',
                'country': 'United States',
                'postal_code': '33131',
                'bedrooms': 3,
                'bathrooms': 3,
                'max_guests': 6,
                'area_sqft': 2500,
                'price_per_night': Decimal('400.00'),
                'cleaning_fee': Decimal('100.00'),
                'security_deposit': Decimal('500.00'),
                'min_nights': 3,
                'max_nights': 21,
                'amenity_indices': [0, 1, 3, 5, 7, 9, 10, 12, 16, 17, 18]
            },
            {
                'host': self.hosts[2],
                'title': 'Rustic Mountain Cabin with Hot Tub',
                'description': 'Disconnect from the digital world in this authentic log cabin nestled in the mountains. Features include a stone fireplace, wrap-around deck with hot tub, and hiking trails right from the door.',
                'category': categories[7],
                'property_type': 'entire_place',
                'address': '147 Pine Ridge Road',
                'city': 'Aspen',
                'state': 'Colorado',
                'country': 'United States',
                'postal_code': '81611',
                'bedrooms': 2,
                'bathrooms': 1,
                'max_guests': 4,
                'area_sqft': 900,
                'price_per_night': Decimal('275.00'),
                'cleaning_fee': Decimal('80.00'),
                'security_deposit': Decimal('300.00'),
                'min_nights': 2,
                'max_nights': 14,
                'amenity_indices': [0, 1, 4, 8, 10, 14, 15]
            },
            {
                'host': self.hosts[3],
                'title': 'Beachfront Apartment with Ocean Views',
                'description': 'Wake up to the sound of waves in this stunning beachfront apartment. Direct beach access, panoramic ocean views from every room, and a private balcony make this the ultimate beach vacation rental.',
                'category': categories[0],
                'property_type': 'entire_place',
                'address': '246 Beachfront Drive, Unit 8A',
                'city': 'San Diego',
                'state': 'California',
                'country': 'United States',
                'postal_code': '92109',
                'bedrooms': 2,
                'bathrooms': 2,
                'max_guests': 4,
                'area_sqft': 1100,
                'price_per_night': Decimal('220.00'),
                'cleaning_fee': Decimal('70.00'),
                'security_deposit': Decimal('250.00'),
                'min_nights': 3,
                'max_nights': 21,
                'amenity_indices': [0, 1, 2, 3, 5, 10, 12, 19]
            },
            {
                'host': self.hosts[4],
                'title': 'Historic Brownstone in Greenwich Village',
                'description': 'Experience New York like a local in this beautifully preserved 19th-century brownstone in the heart of Greenwich Village. Original details blend with modern amenities.',
                'category': categories[1],
                'property_type': 'entire_place',
                'address': '135 Washington Square West',
                'city': 'New York',
                'state': 'New York',
                'country': 'United States',
                'postal_code': '10011',
                'bedrooms': 3,
                'bathrooms': 2,
                'max_guests': 6,
                'area_sqft': 1750,
                'price_per_night': Decimal('320.00'),
                'cleaning_fee': Decimal('85.00'),
                'security_deposit': Decimal('400.00'),
                'min_nights': 3,
                'max_nights': 30,
                'amenity_indices': [0, 1, 2, 4, 5, 15, 16]
            }
        ]
        
        self.accommodations = []
        for acc_data in accommodations_data:
            amenity_indices = acc_data.pop('amenity_indices')
            
            accommodation = Accommodation.objects.create(
                status='active',
                is_available=True,
                **acc_data
            )
            
            # Add amenities
            selected_amenities = [amenities[i] for i in amenity_indices]
            accommodation.amenities.set(selected_amenities)
            
            self.accommodations.append(accommodation)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(accommodations_data)} accommodations'))

    def create_bookings(self):
        """Create sample bookings"""
        self.stdout.write('Creating bookings...')
        
        self.bookings = []
        
        # Create completed bookings (past dates)
        for i in range(15):
            guest = random.choice(self.guests)
            accommodation = random.choice(self.accommodations)
            
            # Avoid same guest booking same accommodation multiple times for reviews
            existing_bookings = [b for b in self.bookings if b.guest == guest and b.accommodation == accommodation]
            if existing_bookings:
                continue
            
            # Past dates
            check_in = timezone.now().date() - timedelta(days=random.randint(30, 180))
            check_out = check_in + timedelta(days=random.randint(2, 7))
            
            nights = (check_out - check_in).days
            accommodation_cost = nights * accommodation.price_per_night
            cleaning_fee = accommodation.cleaning_fee or Decimal('0')
            service_fee = accommodation_cost * Decimal('0.10')
            taxes = (accommodation_cost + service_fee) * Decimal('0.08')
            total_cost = accommodation_cost + cleaning_fee + service_fee + taxes
            
            booking = Booking.objects.create(
                guest=guest,
                accommodation=accommodation,
                check_in_date=check_in,
                check_out_date=check_out,
                num_guests=random.randint(1, accommodation.max_guests),
                nights=nights,
                accommodation_cost=accommodation_cost,
                cleaning_fee=cleaning_fee,
                service_fee=service_fee,
                taxes=taxes,
                total_cost=total_cost,
                status='completed',
                special_requests=random.choice([
                    'Late check-in please',
                    'Ground floor preferred',
                    'Quiet room needed',
                    'Early check-out',
                    '',
                    'Anniversary celebration'
                ])
            )
            self.bookings.append(booking)
        
        # Create confirmed future bookings
        for i in range(8):
            guest = random.choice(self.guests)
            accommodation = random.choice(self.accommodations)
            
            # Future dates
            check_in = timezone.now().date() + timedelta(days=random.randint(5, 60))
            check_out = check_in + timedelta(days=random.randint(2, 10))
            
            nights = (check_out - check_in).days
            accommodation_cost = nights * accommodation.price_per_night
            cleaning_fee = accommodation.cleaning_fee or Decimal('0')
            service_fee = accommodation_cost * Decimal('0.10')
            taxes = (accommodation_cost + service_fee) * Decimal('0.08')
            total_cost = accommodation_cost + cleaning_fee + service_fee + taxes
            
            booking = Booking.objects.create(
                guest=guest,
                accommodation=accommodation,
                check_in_date=check_in,
                check_out_date=check_out,
                num_guests=random.randint(1, accommodation.max_guests),
                nights=nights,
                accommodation_cost=accommodation_cost,
                cleaning_fee=cleaning_fee,
                service_fee=service_fee,
                taxes=taxes,
                total_cost=total_cost,
                status='confirmed',
                special_requests=random.choice([
                    'Airport pickup needed',
                    'Baby crib required',
                    'Extra towels please',
                    'Business traveler',
                    '',
                    'Pet traveling with us'
                ])
            )
            self.bookings.append(booking)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(self.bookings)} bookings'))

    def create_reviews(self):
        """Create sample reviews for completed bookings - FIXED VERSION"""
        self.stdout.write('Creating reviews...')
        
        # Get completed bookings
        completed_bookings = [b for b in self.bookings if b.status == 'completed']
        
        review_templates = [
            {
                'title': 'Amazing stay!',
                'comment': 'The property exceeded all my expectations. The host was incredibly responsive and the location was perfect. Would definitely stay here again!',
                'ratings': {'overall': 5, 'cleanliness': 5, 'communication': 5, 'location': 5, 'value': 5}
            },
            {
                'title': 'Great location, comfortable stay',
                'comment': 'Perfect location for exploring the city. The property was exactly as described and the host provided excellent recommendations.',
                'ratings': {'overall': 4, 'cleanliness': 5, 'communication': 4, 'location': 5, 'value': 4}
            },
            {
                'title': 'Beautiful property with stunning views',
                'comment': 'This place is absolutely gorgeous! Every detail was thoughtfully considered. The kitchen was fully equipped and we enjoyed our stay immensely.',
                'ratings': {'overall': 5, 'cleanliness': 5, 'communication': 5, 'location': 4, 'value': 4}
            },
            {
                'title': 'Perfect for families',
                'comment': 'Our family had a wonderful time here. The host thought of everything and provided a safe, comfortable environment for our children.',
                'ratings': {'overall': 5, 'cleanliness': 4, 'communication': 5, 'location': 4, 'value': 5}
            },
            {
                'title': 'Clean and convenient',
                'comment': 'Simple, clean, and exactly what we needed for our business trip. Check-in was seamless and the location made everything accessible.',
                'ratings': {'overall': 4, 'cleanliness': 5, 'communication': 4, 'location': 4, 'value': 4}
            },
            {
                'title': 'Unique and charming',
                'comment': 'This property has so much character! The historic details combined with modern amenities created a perfect blend of old and new.',
                'ratings': {'overall': 4, 'cleanliness': 4, 'communication': 5, 'location': 4, 'value': 4}
            },
            {
                'title': 'Luxury at its finest',
                'comment': 'If you\'re looking for a luxury experience, this is it! Every aspect screams quality and attention to detail. Worth every penny!',
                'ratings': {'overall': 5, 'cleanliness': 5, 'communication': 4, 'location': 5, 'value': 4}
            },
            {
                'title': 'Good value for money',
                'comment': 'Great affordable option in a prime location. The property was clean and comfortable. Perfect for budget-conscious travelers.',
                'ratings': {'overall': 4, 'cleanliness': 4, 'communication': 4, 'location': 5, 'value': 5}
            },
            {
                'title': 'Peaceful retreat',
                'comment': 'Exactly what we needed to disconnect and recharge. Beautiful setting, very quiet and private. Perfect for a relaxing getaway.',
                'ratings': {'overall': 4, 'cleanliness': 4, 'communication': 3, 'location': 5, 'value': 4}
            },
            {
                'title': 'Modern and stylish',
                'comment': 'Like something out of a design magazine! The smart home features were fun and everything was incredibly modern and well-maintained.',
                'ratings': {'overall': 5, 'cleanliness': 5, 'communication': 5, 'location': 4, 'value': 4}
            }
        ]
        
        reviews_created = 0
        guest_accommodation_pairs = set()
        
        # Create reviews ensuring no duplicate guest-accommodation combinations
        for booking in completed_bookings:
            # Create a unique pair identifier
            pair = (booking.guest.id, booking.accommodation.id)
            
            # Skip if this guest has already reviewed this accommodation
            if pair in guest_accommodation_pairs:
                continue
                
            # Add pair to tracking set
            guest_accommodation_pairs.add(pair)
            
            # Select random review template
            review_data = random.choice(review_templates)
            
            try:
                Review.objects.create(
                    guest=booking.guest,
                    accommodation=booking.accommodation,
                    booking=booking,
                    overall_rating=review_data['ratings']['overall'],
                    cleanliness_rating=review_data['ratings']['cleanliness'],
                    communication_rating=review_data['ratings']['communication'],
                    location_rating=review_data['ratings']['location'],
                    value_rating=review_data['ratings']['value'],
                    title=review_data['title'],
                    comment=review_data['comment'],
                    would_recommend=review_data['ratings']['overall'] >= 4,
                    is_published=True,
                    created_at=booking.check_out_date + timedelta(days=random.randint(1, 5))
                )
                reviews_created += 1
                
                # Stop after creating 10 reviews to avoid constraint violations
                if reviews_created >= 10:
                    break
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Skipped review creation: {str(e)}')
                )
                continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {reviews_created} reviews'))

    def display_summary(self):
        """Display summary of created data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('DATABASE POPULATION COMPLETED SUCCESSFULLY!'))
        self.stdout.write('='*60)
        
        self.stdout.write(f"\n📊 Data Summary:")
        self.stdout.write(f"   👥 Users: {User.objects.count()}")
        self.stdout.write(f"   📂 Categories: {Category.objects.count()}")
        self.stdout.write(f"   ⭐ Amenities: {Amenity.objects.count()}")
        self.stdout.write(f"   🏠 Accommodations: {Accommodation.objects.count()}")
        self.stdout.write(f"   📅 Bookings: {Booking.objects.count()}")
        self.stdout.write(f"   💭 Reviews: {Review.objects.count()}")
        
        self.stdout.write(f"\n🔑 Login Credentials:")
        self.stdout.write(f"   🛡️  Admin:  admin@bookingplatform.com     / admin123")
        self.stdout.write(f"   🏠  Host:   john.host@example.com         / password123")
        self.stdout.write(f"   👤  Guest:  david.guest@example.com       / password123")
        
        self.stdout.write(f"\n🚀 Next Steps:")
        self.stdout.write(f"   1. Run: python manage.py runserver")
        self.stdout.write(f"   2. Visit: http://127.0.0.1:8000/")
        self.stdout.write(f"   3. Login with any account above")
        self.stdout.write(f"   4. Upload property images via host dashboard or admin panel")
        self.stdout.write(f"   5. Test booking flows and platform features")
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Your platform is ready to use!'))
        self.stdout.write('='*60)