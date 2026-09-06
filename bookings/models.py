from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from builtins import property as builtin_property


class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    room = models.ForeignKey(
        'properties.Room',
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    check_in = models.DateField()

    check_out = models.DateField()

    guests = models.PositiveIntegerField(
        default=1
    )

    rooms_booked = models.PositiveIntegerField(
        default=1
    )

    price_per_night = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00'))
        ]
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00'))
        ]
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )

    special_requests = models.TextField(
        blank=True,
        null=True
    )

    admin_notes = models.TextField(
        blank=True,
        null=True
    )

    cancellation_reason = models.TextField(
        blank=True,
        null=True
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    confirmed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    checked_in_at = models.DateTimeField(
        blank=True,
        null=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):

        if not self.booking_reference:

            self.booking_reference = (
                f"BK-{uuid.uuid4().hex[:10].upper()}"
            )

        super().save(*args, **kwargs)

    @builtin_property
    def balance(self):

        return self.total_amount - self.amount_paid

    @builtin_property
    def nights(self):

        return (
            self.check_out - self.check_in
        ).days

    def __str__(self):

        return self.booking_reference