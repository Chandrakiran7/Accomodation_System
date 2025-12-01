from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='guest',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username optional by generating from email
        self.fields['username'].required = False
        self.fields['username'].help_text = 'Optional. Will be generated from email if not provided.'

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        """Generate username from email if not provided"""
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        
        if not username and email:
            # Generate username from email
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data['role']
        user.is_verified = False  # Email verification can be added later
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form that accepts email or username"""
    
    username = forms.CharField(
        label='Email or Username',
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email or username',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': True})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Try to authenticate with email first, then username
            self.user_cache = None
            
            # Check if it's an email
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request, 
                        username=user.username, 
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            # If email authentication failed or it's not an email, try username
            if not self.user_cache:
                self.user_cache = authenticate(
                    self.request, 
                    username=username, 
                    password=password
                )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class UserProfileExtendedForm(forms.ModelForm):
    """Form for editing extended profile information"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'address', 'city', 'country', 'postal_code', 
                 'emergency_contact', 'emergency_phone']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
        }
