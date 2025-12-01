from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:booking_id>/', views.ReviewCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='delete'),
    path('<int:pk>/respond/', views.ReviewResponseCreateView.as_view(), name='respond'),
    
    # Review lists
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('accommodation/<int:accommodation_id>/', views.accommodation_reviews, name='accommodation_reviews'),
    
    # AJAX endpoints
    path('<int:pk>/toggle-helpful/', views.toggle_helpful, name='toggle_helpful'),
    path('<int:pk>/report/', views.report_review, name='report_review'),
]
