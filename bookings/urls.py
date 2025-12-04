from django.urls import path
from . import views
from .views import BookingDetailView

app_name = "bookings"

urlpatterns = [
    # ✅ CREATE BOOKING
    path("create/<int:accommodation_id>/", views.BookingCreateView.as_view(), name="create"),

    # ✅ VIEW BOOKING
    path("<int:pk>/", BookingDetailView.as_view(), name="detail"),

    # ✅ GUEST BOOKINGS
    path("my-bookings/", views.MyBookingsView.as_view(), name="my_bookings"),
    path("<int:pk>/edit/", views.edit_booking, name="edit"),
    path("<int:pk>/delete/", views.delete_booking, name="delete"),

    # ✅ HOST BOOKINGS
    path("host-bookings/", views.host_bookings, name="host_bookings"),

    # ✅ HOST ACTIONS (FIXED → FUNCTION VIEWS)
    path("<int:pk>/confirm/", views.confirm_booking, name="confirm"),
    path("<int:pk>/reject/", views.reject_booking, name="reject"),

    # ✅ AJAX
    path("check-availability/", views.check_availability, name="check_availability"),
]
