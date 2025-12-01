from django.contrib import admin
from .models import Booking, Payment, BookingMessage


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_id', 'created_at')


class BookingMessageInline(admin.TabularInline):
    model = BookingMessage
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'guest', 'accommodation', 'check_in_date', 'check_out_date', 'status', 'total_cost')
    list_filter = ('status', 'check_in_date', 'created_at', 'is_cancelled')
    search_fields = ('booking_id', 'guest__email', 'accommodation__title', 'confirmation_code')
    raw_id_fields = ('guest', 'accommodation')
    readonly_fields = ('booking_id', 'nights', 'created_at', 'updated_at')
    inlines = [PaymentInline, BookingMessageInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'guest', 'accommodation', 'status', 'confirmation_code')
        }),
        ('Dates', {
            'fields': ('check_in_date', 'check_out_date', 'nights')
        }),
        ('Guest Details', {
            'fields': ('num_guests', 'guest_names', 'special_requests')
        }),
        ('Pricing', {
            'fields': ('accommodation_cost', 'cleaning_fee', 'service_fee', 'taxes', 'total_cost')
        }),
        ('Cancellation', {
            'fields': ('is_cancelled', 'cancelled_at', 'cancellation_reason', 'cancellation_notes', 'refund_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'booking__booking_id', 'transaction_id')
    raw_id_fields = ('booking',)
    readonly_fields = ('payment_id', 'created_at', 'updated_at')


@admin.register(BookingMessage)
class BookingMessageAdmin(admin.ModelAdmin):
    list_display = ('booking', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('booking__booking_id', 'sender__email')
    raw_id_fields = ('booking', 'sender')

