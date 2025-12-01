from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, UserProfile
from accommodations.models import Accommodation
from bookings.models import Booking
from reviews.models import Review


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view that redirects based on user role"""
    template_name = 'dashboard/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.role == 'host':
            return redirect('dashboard:host')
        else:
            return redirect('dashboard:guest')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'dashboard/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'bio': f"Hello! I'm {user.first_name}."}
        )
        context['profile'] = profile
        context['profile_user'] = user
        
        # Basic stats
        context['member_since'] = user.date_joined
        context['total_bookings'] = Booking.objects.filter(guest=user).count()
        
        if user.role == 'host':
            # Host-specific stats
            user_accommodations = Accommodation.objects.filter(host=user)
            context['total_properties'] = user_accommodations.count()
            context['active_properties'] = user_accommodations.filter(
                status='active', is_available=True
            ).count()
            context['total_reviews'] = Review.objects.filter(
                accommodation__host=user
            ).count()
            context['average_rating'] = Review.objects.filter(
                accommodation__host=user
            ).aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
        
        # Recent activity
        context['recent_bookings'] = Booking.objects.filter(
            guest=user
        ).select_related('accommodation').order_by('-created_at')[:5]
        
        return context


class HostDashboardView(LoginRequiredMixin, TemplateView):
    """Host-specific dashboard"""
    template_name = 'dashboard/host_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'host':
            messages.error(request, 'Access denied. You must be a host to view this page.')
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get host's accommodations
        accommodations = Accommodation.objects.filter(host=user)
        context['accommodations'] = accommodations.order_by('-created_at')
        
        # Property statistics
        context['stats'] = {
            'total_properties': accommodations.count(),
            'active_properties': accommodations.filter(status='active', is_available=True).count(),
            'pending_properties': accommodations.filter(status='pending').count(),
            'inactive_properties': accommodations.filter(is_available=False).count(),
        }
        
        # Booking statistics
        all_bookings = Booking.objects.filter(accommodation__host=user)
        context['booking_stats'] = {
            'total_bookings': all_bookings.count(),
            'pending_bookings': all_bookings.filter(status='pending').count(),
            'confirmed_bookings': all_bookings.filter(status='confirmed').count(),
            'completed_bookings': all_bookings.filter(status='completed').count(),
            'cancelled_bookings': all_bookings.filter(status='cancelled').count(),
        }
        
        # Revenue statistics
        completed_bookings = all_bookings.filter(status='completed')
        context['revenue_stats'] = {
            'total_revenue': completed_bookings.aggregate(
                total=Sum('total_cost')
            )['total'] or 0,
            'this_month_revenue': completed_bookings.filter(
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month
            ).aggregate(total=Sum('total_cost'))['total'] or 0,
        }
        
        # Review statistics
        all_reviews = Review.objects.filter(accommodation__host=user, is_published=True)
        context['review_stats'] = {
            'total_reviews': all_reviews.count(),
            'average_rating': all_reviews.aggregate(
                avg_rating=Avg('overall_rating')
            )['avg_rating'] or 0,
            'five_star_reviews': all_reviews.filter(overall_rating=5).count(),
        }
        
        # Recent bookings
        context['recent_bookings'] = all_bookings.select_related(
            'guest', 'accommodation'
        ).order_by('-created_at')[:10]
        
        # Recent reviews
        context['recent_reviews'] = all_reviews.select_related(
            'guest', 'accommodation'
        ).order_by('-created_at')[:5]
        
        # Upcoming check-ins/check-outs
        today = timezone.now().date()
        context['upcoming_checkins'] = all_bookings.filter(
            check_in_date=today,
            status='confirmed'
        ).select_related('guest', 'accommodation')
        
        context['upcoming_checkouts'] = all_bookings.filter(
            check_out_date=today,
            status='checked_in'
        ).select_related('guest', 'accommodation')
        
        return context


class GuestDashboardView(LoginRequiredMixin, TemplateView):
    """Guest-specific dashboard"""
    template_name = 'dashboard/guest_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's bookings
        bookings = Booking.objects.filter(guest=user).select_related(
            'accommodation__host', 'accommodation__category'
        ).prefetch_related('accommodation__images')
        
        context['bookings'] = bookings.order_by('-created_at')
        
        # Booking statistics
        context['booking_stats'] = {
            'total_bookings': bookings.count(),
            'upcoming_bookings': bookings.filter(
                status__in=['confirmed', 'checked_in'],
                check_in_date__gte=timezone.now().date()
            ).count(),
            'past_bookings': bookings.filter(
                status__in=['completed', 'checked_out']
            ).count(),
            'cancelled_bookings': bookings.filter(status='cancelled').count(),
        }
        
        # Spending statistics
        completed_bookings = bookings.filter(status='completed')
        context['spending_stats'] = {
            'total_spent': completed_bookings.aggregate(
                total=Sum('total_cost')
            )['total'] or 0,
            'average_booking_cost': completed_bookings.aggregate(
                avg=Avg('total_cost')
            )['avg'] or 0,
        }
        
        # Review statistics
        user_reviews = Review.objects.filter(guest=user)
        context['review_stats'] = {
            'reviews_written': user_reviews.count(),
            'average_rating_given': user_reviews.aggregate(
                avg_rating=Avg('overall_rating')
            )['avg_rating'] or 0,
        }
        
        # Categorize bookings
        today = timezone.now().date()
        
        context['upcoming_bookings'] = bookings.filter(
            status__in=['confirmed', 'checked_in'],
            check_in_date__gte=today
        ).order_by('check_in_date')[:5]
        
        context['past_bookings'] = bookings.filter(
            status__in=['completed', 'checked_out']
        ).order_by('-check_out_date')[:5]
        
        # Current bookings (checked in)
        context['current_bookings'] = bookings.filter(
            status='checked_in',
            check_in_date__lte=today,
            check_out_date__gt=today
        )
        
        # Bookings that need reviews
        context['bookings_to_review'] = bookings.filter(
            status='completed'
        ).exclude(
            id__in=Review.objects.filter(guest=user).values_list('booking_id', flat=True)
        )[:3]
        
        # Travel statistics
        unique_cities = completed_bookings.values_list(
            'accommodation__city', flat=True
        ).distinct()
        
        unique_countries = completed_bookings.values_list(
            'accommodation__country', flat=True
        ).distinct()
        
        context['travel_stats'] = {
            'cities_visited': len(set(unique_cities)),
            'countries_visited': len(set(unique_countries)),
            'total_nights': completed_bookings.aggregate(
                total_nights=Sum('nights')
            )['total_nights'] or 0,
        }
        
        return context


@login_required
def switch_role(request):
    """Allow users to switch between guest and host roles"""
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['guest', 'host']:
            request.user.role = new_role
            request.user.save()
            
            if new_role == 'host':
                messages.success(request, 'Welcome to hosting! You can now add properties and start earning.')
                return redirect('dashboard:host')
            else:
                messages.success(request, 'You are now browsing as a guest. Start exploring amazing places!')
                return redirect('dashboard:guest')
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('dashboard:profile')

