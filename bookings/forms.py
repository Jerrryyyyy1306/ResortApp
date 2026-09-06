from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Booking


class BookingAdminForm(forms.ModelForm):

    class Meta:

        model = Booking

        fields = [
            'client',
            'property',
            'room',
            'check_in',
            'check_out',
            'guests',
            'rooms_booked',
            'price_per_night',
            'total_amount',
            'amount_paid',
            'status',
            'payment_status',
            'special_requests',
            'admin_notes',
            'cancellation_reason',
            'rejection_reason',
        ]

        widgets = {

            'check_in': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'check_out': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'special_requests': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder':
                        'Guest special requests...'
                }
            ),

            'admin_notes': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder':
                        'Internal admin notes...'
                }
            ),

            'cancellation_reason': forms.Textarea(
                attrs={
                    'rows': 3
                }
            ),

            'rejection_reason': forms.Textarea(
                attrs={
                    'rows': 3
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        check_in = cleaned_data.get(
            'check_in'
        )

        check_out = cleaned_data.get(
            'check_out'
        )

        amount_paid = cleaned_data.get(
            'amount_paid'
        )

        total_amount = cleaned_data.get(
            'total_amount'
        )

        if check_in and check_out:

            if check_out <= check_in:

                raise ValidationError(
                    'Check-out date must be after check-in date.'
                )

        if (
            amount_paid is not None
            and total_amount is not None
        ):

            if amount_paid > total_amount:

                raise ValidationError(
                    'Amount paid cannot be greater than total amount.'
                )

        return cleaned_data