from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = [
            'booking',
            'client',
            'amount',
            'payment_method',
            'status',
            'transaction_id',
            'notes',
            'paid_at'
        ]

        widgets = {

            'booking': forms.Select(
                attrs={
                    'class': 'payment-select'
                }
            ),

            'client': forms.Select(
                attrs={
                    'class': 'payment-select'
                }
            ),

            'amount': forms.NumberInput(
                attrs={
                    'class': 'payment-input',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': 'Enter amount'
                }
            ),

            'payment_method': forms.Select(
                attrs={
                    'class': 'payment-select'
                }
            ),

            'status': forms.Select(
                attrs={
                    'class': 'payment-select'
                }
            ),

            'transaction_id': forms.TextInput(
                attrs={
                    'class': 'payment-input',
                    'placeholder': 'Transaction ID'
                }
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'payment-textarea',
                    'rows': 4,
                    'placeholder': 'Payment notes...'
                }
            ),

            'paid_at': forms.DateTimeInput(
                attrs={
                    'class': 'payment-input',
                    'type': 'datetime-local'
                }
            ),
        }


    def clean(self):

        cleaned_data = super().clean()

        booking = cleaned_data.get('booking')
        client = cleaned_data.get('client')
        amount = cleaned_data.get('amount')

        if booking and client:

            if booking.client != client:

                raise forms.ValidationError(
                    'The selected client does not belong to this booking.'
                )

        if booking and amount:

            existing_paid = sum(
                payment.amount
                for payment in booking.payments.filter(
                    status='successful'
                )
                if self.instance.pk != payment.pk
            )

            remaining = booking.total_amount - existing_paid

            if amount > remaining:

                raise forms.ValidationError(
                    f'Payment cannot exceed the outstanding balance '
                    f'of {remaining:.2f}.'
                )

        return cleaned_data