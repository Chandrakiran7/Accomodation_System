from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

User = get_user_model()


class Review(models.Model):
    """
    Reviews for accommodations by guests
    """
    # Relationships
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest_reviews')
    accommodation = models.ForeignKey(
        'accommodations.Accommodation',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True
    )
    
    # Rating (1-5 stars)
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Detailed Ratings
    cleanliness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    location_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Review Content
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Recommendations
    would_recommend = models.BooleanField(default=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('guest', 'accommodation')  # One review per guest per accommodation
        indexes = [
            models.Index(fields=['accommodation', 'is_published']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Review by {self.guest.get_full_name()} for {self.accommodation.title}"

    def get_absolute_url(self):
        return reverse('review:detail', kwargs={'pk': self.pk})

    @property
    def average_detailed_rating(self):
        """Calculate average of detailed ratings"""
        ratings = [
            self.cleanliness_rating,
            self.communication_rating,
            self.location_rating,
            self.value_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return round(sum(valid_ratings) / len(valid_ratings), 1)
        return self.overall_rating


class ReviewResponse(models.Model):
    """
    Host responses to guest reviews
    """
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='host_response'
    )
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response by {self.host.get_full_name()} to review #{self.review.id}"


class ReviewHelpful(models.Model):
    """
    Track helpful votes for reviews
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        helpful_text = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.get_full_name()} found review #{self.review.id} {helpful_text}"


class ReviewReport(models.Model):
    """
    Reports for inappropriate reviews
    """
    REPORT_REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Review'),
        ('personal_info', 'Contains Personal Information'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES)
    description = models.TextField(blank=True)
    
    # Admin Review
    is_reviewed = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    action_taken = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'reporter')

    def __str__(self):
        return f"Report by {self.reporter.get_full_name()} for review #{self.review.id}"


class HostReview(models.Model):
    """
    Reviews of guests by hosts (optional feature)
    """
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host_reviews')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='guest_review'
    )
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Detailed Ratings
    cleanliness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    respect_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Review Content
    comment = models.TextField(blank=True)
    would_host_again = models.BooleanField(default=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('host', 'guest', 'booking')

    def __str__(self):
        return f"Guest review by {self.host.get_full_name()} for {self.guest.get_full_name()}"

