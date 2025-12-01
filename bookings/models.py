from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Booking(models.Model):
    """
    Main booking model for reservations
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    CANCELLATION_REASON_CHOICES = [
        ('guest_request', 'Guest Request'),
        ('host_cancelled', 'Host Cancelled'),
        ('payment_failed', 'Payment Failed'),
        ('policy_violation', 'Policy Violation'),
        ('emergency', 'Emergency'),
    ]

    # Booking Information
    booking_id = models.CharField(max_length=20, unique=True)
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    accommodation = models.ForeignKey(
        'accommodations.Accommodation', 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    
    # Dates and Duration
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    nights = models.PositiveIntegerField()
    
    # Guest Details
    num_guests = models.PositiveIntegerField()
    guest_names = models.JSONField(default=list)  # Store additional guest names
    special_requests = models.TextField(blank=True)
    
    # Pricing
    accommodation_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cleaning_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    taxes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmation_code = models.CharField(max_length=10, blank=True)
    
    # Cancellation
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(
        max_length=20, 
        choices=CANCELLATION_REASON_CHOICES, 
        blank=True
    )
    cancellation_notes = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['guest', 'status']),
            models.Index(fields=['accommodation', 'check_in_date']),
            models.Index(fields=['booking_id']),
        ]

    def __str__(self):
        return f"Booking {self.booking_id} - {self.accommodation.title}"

    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Generate unique booking ID
            import string
            import random
            self.booking_id = 'BK' + ''.join(random.choices(string.digits, k=8))
        
        if not self.confirmation_code and self.status == 'confirmed':
            # Generate confirmation code
            import string
            import random
            self.confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Calculate nights
        self.nights = (self.check_out_date - self.check_in_date).days
        
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        """Check if booking can be cancelled based on policy"""
        if self.status in ['cancelled', 'checked_in', 'checked_out', 'completed']:
            return False
        
        # Add cancellation policy logic here
        days_until_checkin = (self.check_in_date - timezone.now().date()).days
        return days_until_checkin >= 1  # Can cancel up to 1 day before

    @property
    def is_current(self):
        """Check if guest is currently staying"""
        today = timezone.now().date()
        return (self.check_in_date <= today <= self.check_out_date and 
                self.status in ['confirmed', 'checked_in'])

    def calculate_refund(self):
        """Calculate refund amount based on cancellation policy"""
        if not self.can_cancel:
            return Decimal('0.00')
        
        days_until_checkin = (self.check_in_date - timezone.now().date()).days
        
        # Simple cancellation policy - can be made more complex
        if days_until_checkin >= 7:
            return self.total_cost  # Full refund
        elif days_until_checkin >= 3:
            return self.total_cost * Decimal('0.5')  # 50% refund
        else:
            return Decimal('0.00')  # No refund


class Payment(models.Model):
    """
    Payment records for bookings
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    payment_id = models.CharField(max_length=50, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Transaction Details
    transaction_id = models.CharField(max_length=100, blank=True)
    processor_response = models.JSONField(default=dict, blank=True)
    
    # Refund Information
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)
    
    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate unique payment ID
            import string
            import random
            self.payment_id = 'PAY' + ''.join(random.choices(string.digits, k=10))
        super().save(*args, **kwargs)


class BookingMessage(models.Model):
    """
    Messages between guests and hosts regarding bookings
    """
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} - {self.booking.booking_id}"

