from django.contrib import admin
from .models import Category, Amenity, Accommodation, AccommodationImage, UnavailableDate


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


class AccommodationImageInline(admin.TabularInline):
    model = AccommodationImage
    extra = 1


class UnavailableDateInline(admin.TabularInline):
    model = UnavailableDate
    extra = 0


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'city', 'status', 'price_per_night', 'created_at')
    list_filter = ('status', 'category', 'property_type', 'city', 'featured')
    search_fields = ('title', 'host__email', 'city', 'address')
    raw_id_fields = ('host',)
    filter_horizontal = ('amenities',)
    inlines = [AccommodationImageInline, UnavailableDateInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'host', 'category', 'property_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'max_guests', 'area_sqft')
        }),
        ('Pricing', {
            'fields': ('price_per_night', 'cleaning_fee', 'security_deposit')
        }),
        ('Availability', {
            'fields': ('min_nights', 'max_nights', 'advance_booking_days')
        }),
        ('Features', {
            'fields': ('amenities',)
        }),
        ('Policies', {
            'fields': ('house_rules', 'cancellation_policy', 'check_in_time', 'check_out_time')
        }),
        ('Status', {
            'fields': ('status', 'is_available', 'featured')
        }),
    )


@admin.register(AccommodationImage)
class AccommodationImageAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    raw_id_fields = ('accommodation',)


@admin.register(UnavailableDate)
class UnavailableDateAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'date', 'reason', 'created_at')
    list_filter = ('reason', 'date')
    raw_id_fields = ('accommodation',)

