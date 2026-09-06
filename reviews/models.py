from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from builtins import property as builtin_property


class Review(models.Model):

    MODERATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    # Customer who wrote the review
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    # Resort / Guest House being reviewed
    # NOTE: field is intentionally called "property"
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    # Optional booking associated with the review
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )

    # Rating from 1 to 5
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    # Review title
    title = models.CharField(
        max_length=150
    )

    # Review content
    comment = models.TextField()

    # Admin moderation status
    status = models.CharField(
        max_length=20,
        choices=MODERATION_STATUS,
        default='pending'
    )

    # Whether an admin has flagged the review
    is_flagged = models.BooleanField(
        default=False
    )

    # Optional response from administrator
    admin_response = models.TextField(
        blank=True,
        null=True
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    moderated_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.property} - {self.rating}★ - {self.client}"

    @builtin_property
    def stars_display(self):
        """
        Returns:
        ★★★★★
        ★★★★☆
        ★★★☆☆
        etc.
        """
        return '★' * self.rating + '☆' * (5 - self.rating)

    @builtin_property
    def short_comment(self):
        """
        Shortens long review comments for the admin list.
        """
        if len(self.comment) > 100:
            return self.comment[:100] + '...'

        return self.comment