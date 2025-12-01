from django.urls import path
from . import views

app_name = 'accommodations'

urlpatterns = [
    path('', views.AccommodationListView.as_view(), name='list'),
    path('<int:pk>/', views.AccommodationDetailView.as_view(), name='detail'),
    path('search/', views.AccommodationSearchView.as_view(), name='search'),
    path('create/', views.AccommodationCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.AccommodationUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AccommodationDeleteView.as_view(), name='delete'),
    
    # AJAX endpoints
    path('location-suggestions/', views.location_suggestions, name='location_suggestions'),
    path('<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/upload-images/', views.upload_images, name='upload_images'),
    path('delete-image/<int:image_id>/', views.delete_accommodation_image, name='delete_image'),
]