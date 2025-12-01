from django import forms
from .models import Review, ReviewResponse, ReviewReport


class ReviewForm(forms.ModelForm):
    """Form for creating and updating reviews"""
    
    class Meta:
        model = Review
        fields = [
            'overall_rating', 'cleanliness_rating', 'communication_rating',
            'location_rating', 'value_rating', 'title', 'comment', 'would_recommend'
        ]
        widgets = {
            'overall_rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'cleanliness_rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'communication_rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'location_rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'value_rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Summarize your experience'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your experience with future guests...'
            }),
            'would_recommend': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make detailed ratings optional but keep overall rating required
        for field_name in ['cleanliness_rating', 'communication_rating', 'location_rating', 'value_rating']:
            self.fields[field_name].required = False
        
        # Add help text
        self.fields['overall_rating'].help_text = 'How would you rate your overall experience?'
        self.fields['title'].help_text = 'Give your review a title that summarizes your experience'
        self.fields['comment'].help_text = 'Tell other travelers about your stay'


class ReviewResponseForm(forms.ModelForm):
    """Form for host responses to reviews"""
    
    class Meta:
        model = ReviewResponse
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Respond to this review...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['response'].help_text = 'Thank your guest and address any concerns they may have raised'


class ReviewReportForm(forms.ModelForm):
    """Form for reporting inappropriate reviews"""
    
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide additional details about why you are reporting this review...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].help_text = 'Optional: Provide additional context for your report'


class ReviewFilterForm(forms.Form):
    """Form for filtering reviews"""
    
    RATING_CHOICES = [
        ('', 'All Ratings'),
        ('5', '5 Stars'),
        ('4', '4+ Stars'),
        ('3', '3+ Stars'),
        ('2', '2+ Stars'),
        ('1', '1+ Stars'),
    ]
    
    SORT_CHOICES = [
        ('-created_at', 'Most Recent'),
        ('created_at', 'Oldest First'),
        ('-overall_rating', 'Highest Rated'),
        ('overall_rating', 'Lowest Rated'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search reviews...'
        })
    )
