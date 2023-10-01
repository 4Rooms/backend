import logging
import os
from pathlib import Path

from accounts.models import Profile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from files.services.default_avatars import DefaultAvatars

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal for the automatic creation of a user profile when creating a user.
    """

    if created:
        default_avatar = DefaultAvatars().get_random_user_avatar()
        Profile.objects.create(avatar=default_avatar.as_posix(), user=instance)


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

    logger.debug(f"Checking if old avatar should be deleted.")

    # on creation, signal callback won't be triggered
    if instance._state.adding and not instance.pk:
        logger.debug("Avatar is not set yet.")
        return False

    try:
        old_avatar = sender.objects.get(pk=instance.pk).avatar
        if not old_avatar:
            logger.debug("Avatar is not set yet.")
            return False

    except sender.DoesNotExist:
        logger.debug("Profile does not exist.")
        return False

    # if old avatar is not in uploads dir, it is a default avatar
    ava_dir = Path(settings.MEDIA_ROOT) / "avatars" / "uploads"
    if not old_avatar.path.startswith(ava_dir.as_posix()):
        logger.debug(f"Old avatar is a default avatar {old_avatar}")
        return False

    # comparing the new file with the old one
    new_avatar = instance.avatar
    if not old_avatar == new_avatar:
        if os.path.isfile(old_avatar.path):
            logger.debug(f"Deleting old avatar {old_avatar.path}")
            os.remove(old_avatar.path)
