from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accommodations.api import AccommodationViewSet
from bookings.api import BookingViewSet
from reviews.api import ReviewViewSet

router = DefaultRouter()
router.register(r'accommodations', AccommodationViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
