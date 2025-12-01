from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('host/', views.HostDashboardView.as_view(), name='host'),
    path('guest/', views.GuestDashboardView.as_view(), name='guest'),
    path('switch-role/', views.switch_role, name='switch_role'),
]
