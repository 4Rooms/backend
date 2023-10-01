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
