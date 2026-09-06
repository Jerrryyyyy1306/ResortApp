from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review

        fields = [
            'client',
            'property',
            'booking',
            'rating',
            'title',
            'comment',
            'status',
            'is_flagged',
            'admin_response',
        ]

        widgets = {
            'client': forms.Select(attrs={
                'class': 'review-select'
            }),

            'property': forms.Select(attrs={
                'class': 'review-select'
            }),

            'booking': forms.Select(attrs={
                'class': 'review-select'
            }),

            'rating': forms.Select(attrs={
                'class': 'review-select'
            }),

            'title': forms.TextInput(attrs={
                'class': 'review-input',
                'placeholder': 'Review title'
            }),

            'comment': forms.Textarea(attrs={
                'class': 'review-textarea',
                'rows': 6,
                'placeholder': 'Customer review...'
            }),

            'status': forms.Select(attrs={
                'class': 'review-select'
            }),

            'is_flagged': forms.CheckboxInput(attrs={
                'class': 'review-checkbox'
            }),

            'admin_response': forms.Textarea(attrs={
                'class': 'review-textarea',
                'rows': 5,
                'placeholder': 'Optional response from administration...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        client = cleaned_data.get('client')
        booking = cleaned_data.get('booking')
        property_obj = cleaned_data.get('property')

        if booking:
            if client and booking.client != client:
                raise forms.ValidationError(
                    'The selected booking does not belong to the selected client.'
                )

            if property_obj and booking.property != property_obj:
                raise forms.ValidationError(
                    'The selected booking does not belong to the selected property.'
                )

        return cleaned_data