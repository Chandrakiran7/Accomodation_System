from django import forms
from django.core.exceptions import ValidationError
from .models import Accommodation, Category, Amenity


class AccommodationSearchForm(forms.Form):
    """Form for searching accommodations"""
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Where are you going?'
        })
    )
    
    check_in_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    check_out_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    num_guests = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Guests'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="Any category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price'
        })
    )
    
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )


class AccommodationForm(forms.ModelForm):
    """Form for creating/editing accommodations"""
    
    class Meta:
        model = Accommodation
        exclude = ['host', 'status', 'views_count', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your place a catchy title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your place in detail...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Latitude (optional)'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Longitude (optional)'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'max_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'area_sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Square feet (optional)'
            }),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'cleaning_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'security_deposit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'min_nights': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'max_nights': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'advance_booking_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'house_rules': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'House rules for guests...'
            }),
            'cancellation_policy': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cancellation policy...'
            }),
            'check_in_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'check_out_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_time = cleaned_data.get('check_in_time')
        check_out_time = cleaned_data.get('check_out_time')
        min_nights = cleaned_data.get('min_nights')
        max_nights = cleaned_data.get('max_nights')

        # Validate check-in/check-out times
        if check_in_time and check_out_time and check_in_time >= check_out_time:
            raise ValidationError('Check-out time must be after check-in time.')

        # Validate nights
        if min_nights and max_nights and min_nights > max_nights:
            raise ValidationError('Minimum nights cannot be greater than maximum nights.')

        return cleaned_data