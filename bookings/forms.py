from django import forms
from .models import Booking, BookingMessage, Payment
from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'check_in_date',
            'check_out_date',
            'num_guests',
            'special_requests'
        ]

        widgets = {
            'check_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'num_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
            }),

            # ✅ ✅ THIS IS THE CRITICAL FIX ✅ ✅
            'special_requests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Any special requests? (optional)',
            }),
        }



    def __init__(self, *args, **kwargs):
        self.accommodation = kwargs.pop('accommodation', None)
        super().__init__(*args, **kwargs)
        
        if self.accommodation:
            self.fields['num_guests'].widget.attrs['max'] = self.accommodation.max_guests
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        num_guests = cleaned_data.get('num_guests')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError('Check-out date must be after check-in date.')
            
            # Check minimum nights
            if self.accommodation:
                nights = (check_out - check_in).days
                if nights < self.accommodation.min_nights:
                    raise forms.ValidationError(
                        f'Minimum stay is {self.accommodation.min_nights} nights.'
                    )
                if nights > self.accommodation.max_nights:
                    raise forms.ValidationError(
                        f'Maximum stay is {self.accommodation.max_nights} nights.'
                    )
        
        if num_guests and self.accommodation:
            if num_guests > self.accommodation.max_guests:
                raise forms.ValidationError(
                    f'Maximum guests allowed: {self.accommodation.max_guests}'
                )
        
        return cleaned_data


class BookingMessageForm(forms.ModelForm):
    """Form for booking messages"""
    
    class Meta:
        model = BookingMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            })
        }


class PaymentForm(forms.ModelForm):
    """Form for payment processing"""
    
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            })
        }
