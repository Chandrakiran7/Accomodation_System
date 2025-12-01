from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.db import models
from django.db.models import Avg

User = get_user_model()


class Category(models.Model):
    """
    Accommodation categories (e.g., Apartment, House, Villa, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Font icon class
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Amenity(models.Model):
    """
    Available amenities (e.g., WiFi, Pool, Gym, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Font icon class
    category = models.CharField(max_length=50, blank=True)  # e.g., 'basic', 'luxury'
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name


class Accommodation(models.Model):
    """
    Main accommodation model for listings
    """
    PROPERTY_TYPE_CHOICES = [
        ('entire_place', 'Entire Place'),
        ('private_room', 'Private Room'),
        ('shared_room', 'Shared Room'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval'),
        ('suspended', 'Suspended'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accommodations')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='accommodations')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Property Details
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
    area_sqft = models.PositiveIntegerField(null=True, blank=True)
    
    # Pricing
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    cleaning_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Availability
    min_nights = models.PositiveIntegerField(default=1)
    max_nights = models.PositiveIntegerField(default=365)
    advance_booking_days = models.PositiveIntegerField(default=1)
    
    # Features
    amenities = models.ManyToManyField(Amenity, blank=True)
    
    # Rules and Policies
    house_rules = models.TextField(blank=True)
    cancellation_policy = models.TextField(blank=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'status']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.city}"

    def get_absolute_url(self):
        return reverse('accommodation:detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        agg = self.reviews.filter(is_published=True).aggregate(
            avg=Avg('overall_rating')
        )
        avg = agg['avg']
        return round(avg, 1) if avg is not None else None

    @property
    def total_reviews(self):
        return self.reviews.count()

    def is_available_for_dates(self, check_in, check_out):
        """Check if accommodation is available for given dates"""
        from bookings.models import Booking
        overlapping_bookings = Booking.objects.filter(
            accommodation=self,
            status__in=['confirmed', 'checked_in'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        return not overlapping_bookings.exists()


class AccommodationImage(models.Model):
    """
    Images for accommodations
    """
    accommodation = models.ForeignKey(
        Accommodation, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='accommodations/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.accommodation.title} - Image {self.order}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per accommodation
        if self.is_primary:
            AccommodationImage.objects.filter(
                accommodation=self.accommodation, 
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class UnavailableDate(models.Model):
    """
    Dates when accommodation is unavailable
    """
    accommodation = models.ForeignKey(
        Accommodation, 
        on_delete=models.CASCADE, 
        related_name='unavailable_dates'
    )
    date = models.DateField()
    reason = models.CharField(
        max_length=100, 
        choices=[
            ('maintenance', 'Maintenance'),
            ('personal_use', 'Personal Use'),
            ('blocked', 'Blocked by Host'),
        ],
        default='blocked'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('accommodation', 'date')

    def __str__(self):
        return f"{self.accommodation.title} - {self.date} ({self.reason})"

