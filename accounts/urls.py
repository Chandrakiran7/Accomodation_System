from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  # CHANGED: Custom logout view
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('upload-picture/', views.upload_profile_picture, name='upload_picture'),
    path('switch-role/', views.switch_role, name='switch_role'),
]