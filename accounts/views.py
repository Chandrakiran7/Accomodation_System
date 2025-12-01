from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import User, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, CustomAuthenticationForm, UserProfileExtendedForm


class CustomLoginView(LoginView):
    """Custom login view with enhanced functionality"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        if user.role == 'host':
            return reverse_lazy('dashboard:host')
        elif user.role == 'guest':
            return reverse_lazy('dashboard:guest')
        else:
            return reverse_lazy('home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name}!')
        return super().form_valid(form)


class RegisterView(CreateView):
    """User registration view with profile creation"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def get_initial(self):
        """Get initial data for the form"""
        initial = super().get_initial()
        role = self.request.GET.get('role', 'guest')
        if role in ['host', 'guest']:
            initial['role'] = role
        return initial
    
    def form_valid(self, form):
        """Create user and profile"""
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Create user profile
            UserProfile.objects.create(
                user=self.object,
                bio=f"Hello! I'm {self.object.first_name}."
            )
            
            # Auto-login after registration
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(self.request, user)
                messages.success(
                    self.request, 
                    f'Welcome to BookingPlatform, {user.first_name}! Your account has been created successfully.'
                )
                
                # Redirect based on role
                if user.role == 'host':
                    self.success_url = reverse_lazy('dashboard:host')
                else:
                    self.success_url = reverse_lazy('dashboard:guest')
            
            return response
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'bio': f"Hello! I'm {user.first_name}."}
        )
        context['profile'] = profile
        
        # Get user's accommodations if they're a host
        if user.role == 'host':
            from accommodations.models import Accommodation
            context['accommodations'] = Accommodation.objects.filter(host=user)[:3]
        
        # Get user's recent bookings
        from bookings.models import Booking
        context['recent_bookings'] = Booking.objects.filter(guest=user).order_by('-created_at')[:3]
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'profile'):
            context['profile_form'] = UserProfileExtendedForm(
                instance=self.request.user.profile,
                prefix='profile'
            )
        else:
            context['profile_form'] = UserProfileExtendedForm(prefix='profile')
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if hasattr(self.object, 'profile'):
            profile_form = UserProfileExtendedForm(
                request.POST, 
                instance=self.object.profile,
                prefix='profile'
            )
        else:
            profile_form = UserProfileExtendedForm(request.POST, prefix='profile')
        
        if form.is_valid() and profile_form.is_valid():
            form.save()
            
            if hasattr(self.object, 'profile'):
                profile_form.save()
            else:
                profile = profile_form.save(commit=False)
                profile.user = self.object
                profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect(self.success_url)
        else:
            context = self.get_context_data(form=form)
            context['profile_form'] = profile_form
            return self.render_to_response(context)
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)


@login_required
@require_http_methods(["POST"])
def upload_profile_picture(request):
    """AJAX endpoint for profile picture upload"""
    if 'profile_picture' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No file uploaded'})
    
    user = request.user
    user.profile_picture = request.FILES['profile_picture']
    user.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Profile picture updated successfully!',
        'image_url': user.profile_picture.url if user.profile_picture else None
    })


@login_required
def switch_role(request):
    """Allow users to switch between guest and host roles"""
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['guest', 'host']:
            request.user.role = new_role
            request.user.save()
            
            if new_role == 'host':
                messages.success(request, 'Welcome to hosting! You can now add properties.')
                return redirect('dashboard:host')
            else:
                messages.success(request, 'You are now browsing as a guest.')
                return redirect('dashboard:guest')
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('accounts:profile')


class CustomLoginView(LoginView):
    """Custom login view with enhanced functionality"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        if user.is_host:
            return reverse_lazy('dashboard:host')
        elif user.is_guest:
            return reverse_lazy('dashboard:guest')
        else:
            return reverse_lazy('home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name}!')
        return super().form_valid(form)


class RegisterView(CreateView):
    """User registration view with profile creation"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def get_initial(self):
        """Get initial data for the form"""
        initial = super().get_initial()
        role = self.request.GET.get('role', 'guest')
        if role in ['host', 'guest']:
            initial['role'] = role
        return initial
    
    def form_valid(self, form):
        """Create user and profile"""
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Create user profile
            UserProfile.objects.create(
                user=self.object,
                bio=f"Hello! I'm {self.object.first_name}."
            )
            
            # Auto-login after registration
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(self.request, user)
                messages.success(
                    self.request, 
                    f'Welcome to BookingPlatform, {user.first_name}! Your account has been created successfully.'
                )
                
                # Redirect based on role
                if user.is_host:
                    self.success_url = reverse_lazy('dashboard:host')
                else:
                    self.success_url = reverse_lazy('dashboard:guest')
            
            return response
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = getattr(self.request.user, 'profile', None)
        
        # Get user's accommodations if they're a host
        if self.request.user.is_host:
            context['accommodations'] = self.request.user.accommodations.all()[:3]
        
        # Get user's recent bookings
        context['recent_bookings'] = self.request.user.bookings.all()[:3]
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'profile'):
            context['profile_form'] = UserProfileForm(
                instance=self.request.user.profile,
                prefix='profile'
            )
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)


@login_required
@require_http_methods(["POST"])
def upload_profile_picture(request):
    """AJAX endpoint for profile picture upload"""
    if 'profile_picture' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No file uploaded'})
    
    user = request.user
    user.profile_picture = request.FILES['profile_picture']
    user.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Profile picture updated successfully!',
        'image_url': user.profile_picture.url if user.profile_picture else None
    })


@login_required
def switch_role(request):
    """Allow users to switch between guest and host roles"""
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['guest', 'host']:
            request.user.role = new_role
            request.user.save()
            
            if new_role == 'host':
                messages.success(request, 'Welcome to hosting! You can now add properties.')
                return redirect('dashboard:host')
            else:
                messages.success(request, 'You are now browsing as a guest.')
                return redirect('dashboard:guest')
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('accounts:profile')

def logout_view(request):
    """Custom logout view that accepts both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')