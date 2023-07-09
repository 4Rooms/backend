import os

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal for the automatic creation of a user profile when creating a user.
    """

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal for the automatic saving of created user profile when creating a user.
    """

    instance.profile.save()


@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    """
    Delete old avatar when setting up a new one if the old avatar is
    """

    # on creation, signal callback won't be triggered
    if instance._state.adding and not instance.pk:
        return False

    try:
        old_avatar = sender.objects.get(pk=instance.pk).avatar
        if not old_avatar or old_avatar == "default-user-avatar.jpg":
            return False
    except sender.DoesNotExist:
        return False

    # comparing the new file with the old one
    new_avatar = instance.avatar
    if not old_avatar == new_avatar:
        if os.path.isfile(old_avatar.path):
            os.remove(old_avatar.path)
