from django import forms

from .models import Property
from .models import Room
from .models import Amenity
from .models import PropertyImage

class AmenityForm(forms.ModelForm):

    class Meta:
        model = Amenity

        fields = [
            'name',
            'icon',
            'description',
            'is_active',
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Swimming Pool'
                }
            ),

            'icon': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. fa-solid fa-water'
                }
            ),

            'description': forms.TextInput(
                attrs={
                    'placeholder': 'Short description'
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        queryset = Amenity.objects.filter(
            name__iexact=name
        )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise forms.ValidationError(
                'An amenity with this name already exists.'
            )

        return name


class PropertyForm(forms.ModelForm):

    class Meta:

        model = Property

        fields = [
            'owner',
            'name',
            'property_type',
            'description',
            'address',
            'city',
            'province',
            'country',
            'phone',
            'email',
            'website',
            'check_in_time',
            'check_out_time',
            'amenities',
            'status',
            'rejection_reason',
            'suspension_reason',
            'is_featured',
            'is_verified',
            'is_active',
        ]

        widgets = {

            'description': forms.Textarea(
                attrs={
                    'rows': 6
                }
            ),

            'rejection_reason': forms.Textarea(
                attrs={
                    'rows': 4
                }
            ),

            'suspension_reason': forms.Textarea(
                attrs={
                    'rows': 4
                }
            ),

            'check_in_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time'
                }
            ),

            'check_out_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time'
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            'owner'
        ].queryset = self.fields[
            'owner'
        ].queryset.filter(
            profile__role='owner'
        )


class RoomForm(forms.ModelForm):

    class Meta:

        model = Room

        fields = [
            'name',
            'description',
            'max_guests',
            'bed_type',
            'price_per_night',
            'quantity',
            'is_available',
        ]

        widgets = {

            'description': forms.Textarea(
                attrs={
                    'rows': 4
                }
            ),

        }


class PropertyImageForm(forms.ModelForm):

    class Meta:

        model = PropertyImage

        fields = [
            'image',
            'caption',
            'is_primary',
            'display_order',
        ]