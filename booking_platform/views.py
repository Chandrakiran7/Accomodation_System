from django.shortcuts import render
from accommodations.models import Accommodation, Category


def homepage(request):
    """Homepage view with featured accommodations and categories"""
    
    # Get featured accommodations (active, available, and featured)
    featured_accommodations = Accommodation.objects.filter(
        status='active',
        is_available=True,
        featured=True
    ).select_related('host', 'category').prefetch_related('amenities', 'images')[:6]
    
    # If no featured accommodations, show recent ones
    if not featured_accommodations:
        featured_accommodations = Accommodation.objects.filter(
            status='active',
            is_available=True
        ).select_related('host', 'category').prefetch_related('amenities', 'images')[:6]
    
    # Get all active categories with accommodation count
    categories = Category.objects.filter(
        is_active=True
    ).prefetch_related('accommodations')[:6]
    
    context = {
        'featured_accommodations': featured_accommodations,
        'categories': categories,
    }
    
    return render(request, 'home.html', context)


def about(request):
    """About page view"""
    return render(request, 'about.html', {
        'page_title': 'About Us'
    })


def contact(request):
    """Contact page view"""
    return render(request, 'contact.html', {
        'page_title': 'Contact Us'
    })
