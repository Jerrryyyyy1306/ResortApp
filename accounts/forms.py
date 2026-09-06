from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

from .models import Profile
from django.contrib.auth.forms import AuthenticationForm

from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Profile


class ClientRegistrationForm(forms.ModelForm):

    ACCOUNT_TYPE_CHOICES = [
        ('client', 'Client'),
        ('owner', 'Property Owner'),
    ]

    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'First name',
                'autocomplete': 'given-name',
            }
        )
    )

    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'Last name',
                'autocomplete': 'family-name',
            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'Email address',
                'autocomplete': 'email',
            }
        )
    )

    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                'class': 'account-type-options',
            }
        ),
        label='What type of account do you want?'
    )

    password = forms.CharField(
        required=True,
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'Create a password',
                'autocomplete': 'new-password',
            }
        )
    )

    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'Confirm your password',
                'autocomplete': 'new-password',
            }
        )
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]

    # ========================================================
    # FIRST NAME
    # ========================================================

    def clean_first_name(self):

        first_name = self.cleaned_data.get(
            'first_name',
            ''
        ).strip()

        if not first_name:
            raise forms.ValidationError(
                'Please enter your first name.'
            )

        return first_name

    # ========================================================
    # LAST NAME
    # ========================================================

    def clean_last_name(self):

        last_name = self.cleaned_data.get(
            'last_name',
            ''
        ).strip()

        if not last_name:
            raise forms.ValidationError(
                'Please enter your last name.'
            )

        return last_name

    # ========================================================
    # EMAIL
    # ========================================================

    def clean_email(self):

        email = self.cleaned_data.get(
            'email',
            ''
        ).strip().lower()

        if not email:
            raise forms.ValidationError(
                'Please enter your email address.'
            )

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError(
                'Please enter a valid email address.'
            )

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                'An account with this email address already exists.'
            )

        return email

    # ========================================================
    # PASSWORD CONFIRMATION
    # ========================================================

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:

            if password != password_confirm:

                raise forms.ValidationError(
                    'The passwords do not match.'
                )

        return cleaned_data

    # ========================================================
    # SAVE USER
    # ========================================================

    def save(self, commit=True):

        user = super().save(commit=False)

        email = self.cleaned_data['email']

        user.username = email
        user.email = email

        user.set_password(
            self.cleaned_data['password']
        )

        # IMPORTANT:
        # Registered clients and property owners
        # are NOT Django staff users.
        user.is_staff = False
        user.is_superuser = False

        if commit:

            user.save()

            account_type = self.cleaned_data[
                'account_type'
            ]

            profile, created = Profile.objects.get_or_create(
                user=user
            )

            profile.role = account_type

            profile.is_suspended = False

            profile.save()

        return user



class ClientLoginForm(AuthenticationForm):

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'Enter your email',
                'autocomplete': 'email',
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'client-auth-input',
                'placeholder': 'Enter your password',
                'autocomplete': 'current-password',
            }
        )
    )

    def clean_username(self):
        email = self.cleaned_data.get('username', '').strip().lower()
        return email


class AdminUserCreateForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        required=True
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES
    )

    phone = forms.CharField(
        max_length=30,
        required=False
    )

    class Meta:

        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]

    def clean_username(self):

        username = self.cleaned_data['username']

        if User.objects.filter(
            username__iexact=username
        ).exists():

            raise forms.ValidationError(
                'A user with this username already exists.'
            )

        return username

    def clean_email(self):

        email = self.cleaned_data.get('email')

        if email:

            if User.objects.filter(
                email__iexact=email
            ).exists():

                raise forms.ValidationError(
                    'A user with this email already exists.'
                )

        return email

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get(
            'password_confirm'
        )

        if password and password_confirm:

            if password != password_confirm:

                raise forms.ValidationError(
                    'Passwords do not match.'
                )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data['password']
        )

        role = self.cleaned_data['role']

        if role in ['admin', 'staff']:
            user.is_staff = True
        else:
            user.is_staff = False

        if commit:

            user.save()

            profile = user.profile

            profile.role = role
            profile.phone = self.cleaned_data.get(
                'phone',
                ''
            )

            profile.save()

        return user


class AdminUserEditForm(forms.ModelForm):

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES
    )

    phone = forms.CharField(
        max_length=30,
        required=False
    )

    is_suspended = forms.BooleanField(
        required=False
    )

    suspension_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 4
            }
        )
    )

    class Meta:

        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['username'].disabled = True

        try:

            profile = self.instance.profile

            self.fields['role'].initial = profile.role

            self.fields['phone'].initial = profile.phone

            self.fields[
                'is_suspended'
            ].initial = profile.is_suspended

            self.fields[
                'suspension_reason'
            ].initial = profile.suspension_reason

        except Profile.DoesNotExist:

            pass

    def clean_email(self):

        email = self.cleaned_data.get('email')

        if email:

            exists = User.objects.filter(
                email__iexact=email
            ).exclude(
                pk=self.instance.pk
            ).exists()

            if exists:

                raise forms.ValidationError(
                    'Another user already uses this email.'
                )

        return email

    def save(self, commit=True):

        user = super().save(commit=False)

        role = self.cleaned_data['role']

        if role in ['admin', 'staff']:

            user.is_staff = True

        else:

            user.is_staff = False

        if commit:

            user.save()

            profile = user.profile

            profile.role = role

            profile.phone = self.cleaned_data.get(
                'phone',
                ''
            )

            profile.is_suspended = self.cleaned_data.get(
                'is_suspended',
                False
            )

            profile.suspension_reason = self.cleaned_data.get(
                'suspension_reason',
                ''
            )

            profile.save()

        return user


class AdminPasswordChangeForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput,
        min_length=8
    )

    new_password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput,
        min_length=8
    )