from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('ecocash', 'EcoCash'),
        ('onemoney', 'OneMoney'),
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    payment_reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.PROTECT,
        related_name='payments'
    )

    client = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'))
        ]
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHODS
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):

        if not self.payment_reference:
            self.payment_reference = (
                f"PAY-{uuid.uuid4().hex[:12].upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.payment_reference