import logging
import random
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


class DefaultAvatars:
    def __init__(self):
        self._avatars_dir = Path(settings.MEDIA_ROOT) / "avatars"
        self._chat_avatars_dir = self._avatars_dir / "chat"
        self._user_avatars_dir = self._avatars_dir / "user"
        self._deleted_chat_avatars_dir = self._avatars_dir / "deleted_chat"
        self._deleted_user_avatars_dir = self._avatars_dir / "deleted_user"

    def get_random_user_avatar(self):
        avatars = list(self._user_avatars_dir.glob("*"))
        logger.debug(f"Found {len(avatars)} user avatars.")
        if not avatars:
            return None

        random_avatar = random.choice(avatars)
        return random_avatar.relative_to(settings.MEDIA_ROOT)

    def get_chat_avatar(self, room_name):
        avatars = list(self._chat_avatars_dir.glob("*"))
        logger.debug(f"Found {len(avatars)} chat avatars.")
        if not avatars:
            logger.error("No chat avatars found.")
            return None

        avatar = random.choice(avatars)
        if room_name == "games":
            avatar = self._chat_avatars_dir / "chat_image_01.svg"
        elif room_name == "cinema":
            avatar = self._chat_avatars_dir / "chat_image_02.svg"
        elif room_name == "books":
            avatar = self._chat_avatars_dir / "chat_image_03.svg"
        elif room_name == "music":
            avatar = self._chat_avatars_dir / "chat_image_04.svg"
        else:
            logger.error(f"Unknown room name: {room_name}")

        return avatar.relative_to(settings.MEDIA_ROOT)
