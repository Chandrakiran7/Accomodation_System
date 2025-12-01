from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Review


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Create a review"""
    model = Review
    template_name = 'reviews/create.html'
    fields = ['overall_rating', 'title', 'comment']


class ReviewDetailView(DetailView):
    """View review details"""
    model = Review
    template_name = 'reviews/detail.html'


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """Update review"""
    model = Review
    template_name = 'reviews/edit.html'
    fields = ['overall_rating', 'title', 'comment']


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """Delete review"""
    model = Review
    template_name = 'reviews/delete.html'
    success_url = reverse_lazy('home')


class ReviewResponseCreateView(LoginRequiredMixin, CreateView):
    """Host response to review"""
    template_name = 'reviews/respond.html'
    fields = ['response']


@login_required
def toggle_helpful(request, pk):
    """Toggle helpful vote for a review"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'})
    
    from .models import Review, ReviewHelpful
    review = get_object_or_404(Review, pk=pk, is_published=True)
    is_helpful = request.POST.get('helpful') == 'true'
    
    # Prevent self-voting
    if request.user == review.guest:
        return JsonResponse({
            'success': False,
            'message': 'You cannot vote on your own review'
        })
    
    # Get or create vote
    vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': is_helpful}
    )
    
    if not created:
        if vote.is_helpful == is_helpful:
            # Remove vote if clicking same button
            vote.delete()
            vote_status = 'removed'
        else:
            # Change vote
            vote.is_helpful = is_helpful
            vote.save()
            vote_status = 'changed'
    else:
        vote_status = 'added'
    
    # Get updated counts
    helpful_votes = review.helpful_votes.all()
    helpful_count = helpful_votes.filter(is_helpful=True).count()
    not_helpful_count = helpful_votes.filter(is_helpful=False).count()
    
    return JsonResponse({
        'success': True,
        'vote_status': vote_status,
        'helpful_count': helpful_count,
        'not_helpful_count': not_helpful_count,
        'user_vote': vote.is_helpful if vote_status != 'removed' else None
    })


@login_required
def report_review(request, pk):
    """Report a review for inappropriate content"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'})
    
    from .models import Review, ReviewReport
    review = get_object_or_404(Review, pk=pk, is_published=True)
    reason = request.POST.get('reason')
    description = request.POST.get('description', '')
    
    if not reason or reason not in dict(ReviewReport.REPORT_REASON_CHOICES):
        return JsonResponse({'success': False, 'message': 'Invalid reason'})
    
    # Check if user already reported this review
    existing_report = ReviewReport.objects.filter(
        review=review,
        reporter=request.user
    ).first()
    
    if existing_report:
        return JsonResponse({
            'success': False,
            'message': 'You have already reported this review'
        })
    
    # Create report
    ReviewReport.objects.create(
        review=review,
        reporter=request.user,
        reason=reason,
        description=description
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Review reported successfully. We will investigate this matter.'
    })


def accommodation_reviews(request, accommodation_id):
    """List all reviews for an accommodation"""
    from accommodations.models import Accommodation
    from django.core.paginator import Paginator
    from django.db.models import Count, Avg
    
    accommodation = get_object_or_404(
        Accommodation,
        pk=accommodation_id,
        status='active'
    )
    
    reviews = Review.objects.filter(
        accommodation=accommodation,
        is_published=True
    ).select_related('guest').prefetch_related('host_response').order_by('-created_at')
    
    # Calculate review statistics
    review_stats = reviews.aggregate(
        total_reviews=Count('id'),
        average_rating=Avg('overall_rating'),
        average_cleanliness=Avg('cleanliness_rating'),
        average_communication=Avg('communication_rating'),
        average_location=Avg('location_rating'),
        average_value=Avg('value_rating'),
    )
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(overall_rating=i).count()
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'accommodation': accommodation,
        'reviews': page_obj,
        'review_stats': review_stats,
        'rating_distribution': rating_distribution,
        'total_pages': paginator.num_pages,
    }
    
    return render(request, 'reviews/accommodation_reviews.html', context)


@login_required
def my_reviews(request):
    """List current user's reviews"""
    from django.core.paginator import Paginator
    
    reviews = Review.objects.filter(
        guest=request.user
    ).select_related('accommodation', 'booking').order_by('-created_at')
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reviews': page_obj,
        'total_reviews': reviews.count(),
    }
    
    return render(request, 'reviews/my_reviews.html', context)