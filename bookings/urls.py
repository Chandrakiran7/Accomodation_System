from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:accommodation_id>/', views.BookingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('<int:pk>/confirm/', views.BookingConfirmView.as_view(), name='confirm'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    
    # Host bookings
    path('host-bookings/', views.host_bookings, name='host_bookings'),
    
    # AJAX endpoints
    path('check-availability/', views.check_availability, name='check_availability'),
    path('<int:pk>/send-message/', views.send_booking_message, name='send_message'),
]
