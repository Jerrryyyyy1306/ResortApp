from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Amenity(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    icon = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Property(models.Model):

    PROPERTY_TYPES = [
        ('resort', 'Resort'),
        ('lodge', 'Lodge'),
        ('guest_house', 'Guest House'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('draft', 'Draft'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    name = models.CharField(
        max_length=200
    )

    property_type = models.CharField(
        max_length=30,
        choices=PROPERTY_TYPES
    )

    description = models.TextField()

    address = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100
    )

    province = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default='Zimbabwe'
    )

    phone = models.CharField(
        max_length=30
    )

    email = models.EmailField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    check_in_time = models.TimeField(
        null=True,
        blank=True
    )

    check_out_time = models.TimeField(
        null=True,
        blank=True
    )

    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name='properties'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    rejection_reason = models.TextField(
        blank=True
    )

    suspension_reason = models.TextField(
        blank=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    total_reviews = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:

        ordering = [
            '-created_at'
        ]

        indexes = [
            models.Index(
                fields=['status']
            ),
            models.Index(
                fields=['property_type']
            ),
            models.Index(
                fields=['city']
            ),
            models.Index(
                fields=['is_featured']
            ),
        ]

    def __str__(self):
        return self.name


class PropertyImage(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='properties/'
    )

    caption = models.CharField(
        max_length=255,
        blank=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            'display_order',
            '-uploaded_at'
        ]

    def __str__(self):
        return f"{self.property.name} - Image"


class Room(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='rooms'
    )

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    max_guests = models.PositiveIntegerField(
        default=2
    )

    bed_type = models.CharField(
        max_length=100,
        blank=True
    )

    price_per_night = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.property.name} - {self.name}"