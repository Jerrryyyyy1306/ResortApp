from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:

        role = 'client'

        if instance.is_superuser:
            role = 'admin'

        elif instance.is_staff:
            role = 'staff'

        Profile.objects.create(
            user=instance,
            role=role
        )