from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('owner', 'Property Owner'),
        ('client', 'Client'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    is_suspended = models.BooleanField(
        default=False
    )

    suspension_reason = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"