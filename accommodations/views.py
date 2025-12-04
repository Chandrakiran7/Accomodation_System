from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Max
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Accommodation, Category, Amenity
from .forms import AccommodationForm, AccommodationSearchForm


class AccommodationListView(ListView):
    """List view for accommodations with search and filtering"""
    model = Accommodation
    template_name = 'accommodations/list.html'
    context_object_name = 'accommodations'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Accommodation.objects.all()
        
        # Search parameters
        location = self.request.GET.get('location')
        category = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        num_guests = self.request.GET.get('num_guests')
        amenities = self.request.GET.getlist('amenities')
        
        # Apply filters
        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(country__icontains=location) |
                Q(address__icontains=location)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        if num_guests:
            queryset = queryset.filter(max_guests__gte=num_guests)
        
        if amenities:
            for amenity in amenities:
                queryset = queryset.filter(amenities__id=amenity)
        
        # Default ordering
        return queryset.distinct().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['amenities'] = Amenity.objects.filter(is_active=True)
        context['search_form'] = AccommodationSearchForm(self.request.GET)
        
        # Current filters for display
        context['current_filters'] = {
            'location': self.request.GET.get('location', ''),
            'category': self.request.GET.get('category', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'num_guests': self.request.GET.get('num_guests', ''),
            'amenities': self.request.GET.getlist('amenities'),
        }
        
        return context


class AccommodationDetailView(DetailView):
    """Detail view for individual accommodation"""
    model = Accommodation
    template_name = 'accommodations/detail.html'
    context_object_name = 'accommodation'
    
    def get_queryset(self):
        return Accommodation.objects.filter(
            status='active'
        ).select_related('host', 'category').prefetch_related(
            'amenities', 'images', 'reviews__guest'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accommodation = self.object
        
        # Get reviews with pagination
        reviews = accommodation.reviews.filter(is_published=True).order_by('-created_at')
        context['reviews'] = reviews[:5]  # Show first 5 reviews
        context['total_reviews'] = reviews.count()
        
        # Calculate average ratings
        context['average_ratings'] = accommodation.reviews.filter(
            is_published=True
        ).aggregate(
            overall=Avg('overall_rating'),
            cleanliness=Avg('cleanliness_rating'),
            communication=Avg('communication_rating'),
            location=Avg('location_rating'),
            value=Avg('value_rating'),
        )
        
        # Check availability for selected dates
        check_in = self.request.GET.get('check_in_date')
        check_out = self.request.GET.get('check_out_date')
        if check_in and check_out:
            context['is_available'] = accommodation.is_available_for_dates(
                check_in, check_out
            )
            context['check_in_date'] = check_in
            context['check_out_date'] = check_out
        
        # Suggested similar accommodations
        context['similar_accommodations'] = Accommodation.objects.filter(
            category=accommodation.category,
            city=accommodation.city,
            status='active',
            is_available=True
        ).exclude(pk=accommodation.pk)[:3]
        
        return context
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import AccommodationForm

class AccommodationCreateView(LoginRequiredMixin, CreateView):
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'accommodations/create.html'
    success_url = reverse_lazy('accommodations:list')  # ✅ safer than host_dashboard

    def form_valid(self, form):
        property = form.save(commit=False)
        property.host = self.request.user
        property.status = 'active'   # ✅ REQUIRED FIX
        property.is_available = True  # ✅ IF THIS FIELD EXISTS
        property.save()

        messages.success(self.request, "✅ Property added successfully!")
        return redirect(self.success_url)


'''class AccommodationCreateView(LoginRequiredMixin, CreateView):
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'accommodations/create.html'
    success_url = reverse_lazy('host_dashboard')  # ✅ or 'user_dashboard'

    def form_valid(self, form):
        form.instance.host = self.request.user
        messages.success(self.request, "✅ Property added successfully!")
        return super().form_valid(form)   # ✅ THIS LINE IS THE KEY
'''

'''class AccommodationCreateView(LoginRequiredMixin, CreateView):
    """Create view for new accommodation (hosts only)"""
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'accommodations/create.html'
    success_url = reverse_lazy('dashboard:host')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_host:
            messages.error(request, 'You must be a host to create accommodations.')
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.host = self.request.user
        form.instance.status = 'pending'  # Needs admin approval
        messages.success(
            self.request, 
            'Your accommodation has been submitted for review. We\'ll notify you once it\'s approved.'
        )
        return super().form_valid(form)'''


class AccommodationUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for accommodation (host only)"""
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'accommodations/edit.html'
    
    def get_queryset(self):
        return Accommodation.objects.filter(host=self.request.user)
    
    def form_valid(self, form):
        # Handle new image uploads
        if 'new_images' in self.request.FILES:
            from .models import AccommodationImage
            
            # Get the next order number
            max_order = self.object.images.aggregate(Max('order'))['order__max'] or 0
            
            for i, image_file in enumerate(self.request.FILES.getlist('new_images')):
                AccommodationImage.objects.create(
                    accommodation=self.object,
                    image=image_file,
                    caption=f"{self.object.title} - Image {max_order + i + 1}",
                    order=max_order + i + 1,
                    is_primary=(max_order == 0 and i == 0)  # First image is primary if no images exist
                )
        
        messages.success(self.request, 'Accommodation updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('accommodations:detail', kwargs={'pk': self.object.pk})


class AccommodationDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for accommodation (host only)"""
    model = Accommodation
    template_name = 'accommodations/delete.html'
    success_url = reverse_lazy('dashboard:host')
    
    def get_queryset(self):
        return Accommodation.objects.filter(host=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Accommodation deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AccommodationSearchView(ListView):
    """AJAX search view for accommodations"""
    model = Accommodation
    template_name = 'accommodations/search_results.html'
    context_object_name = 'accommodations'
    paginate_by = 12
    
    def get_queryset(self):
        # Similar to AccommodationListView but for AJAX responses
        return AccommodationListView.get_queryset(self)
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            from django.http import JsonResponse
            from django.template.loader import render_to_string
            
            context = self.get_context_data()
            html = render_to_string(
                'accommodations/search_results_partial.html', 
                context, 
                request=request
            )
            
            return JsonResponse({
                'html': html,
                'count': context['paginator'].count if context['paginator'] else 0
            })
        
        return super().get(request, *args, **kwargs)


@require_http_methods(["GET"])
def location_suggestions(request):
    """AJAX endpoint for location search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get unique locations from accommodations
    cities = Accommodation.objects.filter(
        Q(city__icontains=query) | Q(state__icontains=query) | Q(country__icontains=query),
        status='active'
    ).values_list('city', 'state', 'country').distinct()[:10]
    
    suggestions = []
    for city, state, country in cities:
        if state and country:
            suggestion = f"{city}, {state}, {country}"
        elif country:
            suggestion = f"{city}, {country}"
        else:
            suggestion = city
        
        if suggestion not in suggestions:
            suggestions.append(suggestion)
    
    return JsonResponse({'suggestions': suggestions[:10]})


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, pk):
    """Toggle favorite status for accommodation"""
    accommodation = get_object_or_404(Accommodation, pk=pk, status='active')
    
    # This would require a Favorite model - for now, just return success
    return JsonResponse({
        'success': True,
        'is_favorite': False,  # Implement favorite logic when needed
        'message': 'Added to favorites' if False else 'Removed from favorites'
    })


@login_required
@require_http_methods(["POST"])
def upload_images(request, pk):
    """AJAX endpoint for uploading accommodation images"""
    from .models import AccommodationImage
    
    accommodation = get_object_or_404(
        Accommodation, 
        pk=pk, 
        host=request.user
    )
    
    if 'images' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No images uploaded'})
    
    uploaded_images = []
    for image_file in request.FILES.getlist('images'):
        # Get the next order number
        max_order = accommodation.images.aggregate(
            models.Max('order')
        )['order__max'] or 0
        
        acc_image = AccommodationImage.objects.create(
            accommodation=accommodation,
            image=image_file,
            order=max_order + 1
        )
        
        uploaded_images.append({
            'id': acc_image.id,
            'url': acc_image.image.url,
            'is_primary': acc_image.is_primary
        })
    
    return JsonResponse({
        'success': True,
        'message': f'{len(uploaded_images)} images uploaded successfully',
        'images': uploaded_images
    })


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, pk):
    """Toggle favorite status for accommodation"""
    accommodation = get_object_or_404(Accommodation, pk=pk, status='active')
    
    # This would require a Favorite model
    # For now, just return success
    return JsonResponse({
        'success': True,
        'is_favorite': False,  # Implement favorite logic
        'message': 'Added to favorites' if False else 'Removed from favorites'
    })


@require_http_methods(["GET"])
def location_suggestions(request):
    """AJAX endpoint for location search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get unique locations from accommodations
    from django.db.models import Q
    cities = Accommodation.objects.filter(
        Q(city__icontains=query) | Q(state__icontains=query) | Q(country__icontains=query),
        status='active'
    ).values_list('city', 'state', 'country').distinct()[:10]
    
    suggestions = []
    for city, state, country in cities:
        if state and country:
            suggestion = f"{city}, {state}, {country}"
        elif country:
            suggestion = f"{city}, {country}"
        else:
            suggestion = city
        
        if suggestion not in suggestions:
            suggestions.append(suggestion)
    
    return JsonResponse({'suggestions': suggestions[:10]})


@login_required
@require_http_methods(["POST"])
def upload_images(request, pk):
    """AJAX endpoint for uploading accommodation images"""
    accommodation = get_object_or_404(
        Accommodation, 
        pk=pk, 
        host=request.user
    )
    
    if 'images' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No images uploaded'})
    
    from .models import AccommodationImage
    from django.db.models import Max
    
    uploaded_images = []
    for image_file in request.FILES.getlist('images'):
        # Get the next order number
        max_order = accommodation.images.aggregate(
            Max('order')
        )['order__max'] or 0
        
        acc_image = AccommodationImage.objects.create(
            accommodation=accommodation,
            image=image_file,
            order=max_order + 1
        )
        
        uploaded_images.append({
            'id': acc_image.id,
            'url': acc_image.image.url,
            'is_primary': acc_image.is_primary
        })
    
    return JsonResponse({
        'success': True,
        'message': f'{len(uploaded_images)} images uploaded successfully',
        'images': uploaded_images
    })


@login_required
@require_http_methods(["POST"])
def delete_accommodation_image(request, image_id):
    """Delete accommodation image (host only)"""
    from .models import AccommodationImage
    
    try:
        image = get_object_or_404(AccommodationImage, id=image_id)
        
        # Check if user is the host of this accommodation
        if request.user != image.accommodation.host:
            return JsonResponse({'success': False, 'message': 'Permission denied'})
        
        # Delete the image file and database record
        if image.image:
            image.image.delete()
        image.delete()
        
        return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
        
    except AccommodationImage.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Image not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting image: {str(e)}'})