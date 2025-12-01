from django.contrib import admin
from .models import Review, ReviewResponse, ReviewHelpful, ReviewReport, HostReview


class ReviewResponseInline(admin.StackedInline):
    model = ReviewResponse
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('guest', 'accommodation', 'overall_rating', 'is_published', 'created_at')
    list_filter = ('overall_rating', 'is_published', 'is_flagged', 'would_recommend', 'created_at')
    search_fields = ('guest__email', 'accommodation__title', 'title')
    raw_id_fields = ('guest', 'accommodation', 'booking')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ReviewResponseInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('guest', 'accommodation', 'booking', 'title')
        }),
        ('Ratings', {
            'fields': ('overall_rating', 'cleanliness_rating', 'communication_rating', 'location_rating', 'value_rating')
        }),
        ('Review Content', {
            'fields': ('comment', 'would_recommend')
        }),
        ('Status', {
            'fields': ('is_published', 'is_flagged', 'flag_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ('review', 'host', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    raw_id_fields = ('review', 'host')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    raw_id_fields = ('review', 'user')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('review', 'reporter', 'reason', 'is_reviewed', 'created_at')
    list_filter = ('reason', 'is_reviewed', 'created_at')
    search_fields = ('review__title', 'reporter__email')
    raw_id_fields = ('review', 'reporter')
    
    fieldsets = (
        ('Report Information', {
            'fields': ('review', 'reporter', 'reason', 'description')
        }),
        ('Admin Review', {
            'fields': ('is_reviewed', 'admin_notes', 'action_taken')
        }),
    )


@admin.register(HostReview)
class HostReviewAdmin(admin.ModelAdmin):
    list_display = ('host', 'guest', 'rating', 'would_host_again', 'created_at')
    list_filter = ('rating', 'would_host_again', 'is_published', 'created_at')
    raw_id_fields = ('host', 'guest', 'booking')

