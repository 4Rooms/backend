import logging
import math
import mimetypes

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import File
from ..utils import generate_file_name

logger = logging.getLogger(__name__)


class FileUploadService:
    def __init__(self, user: get_user_model(), file_obj):
        self.user = user
        self.file_obj = file_obj

    @transaction.atomic
    def create(self, file_name: str = "", file_type: str = "") -> File:
        if not file_name:
            logger.debug(f"File name not provided. Using {self.file_obj.name}")
            file_name = self.file_obj.name

        if self.file_obj.size > settings.MAX_FILE_SIZE:
            msg = (
                f"File '{file_name}' is too large: {math.ceil(self.file_obj.size / 1024 / 1024)} MB."
                + f" Must be less than {int(settings.MAX_FILE_SIZE / 1024 / 1024)} MB"
            )
            logger.error(msg)
            raise ValidationError(msg)

        if not file_type:
            guessed_file_type, encoding = mimetypes.guess_type(file_name)
            file_type = "" if guessed_file_type is None else guessed_file_type
            logger.debug(f"File type not provided. Using {file_type}")

        obj = File(
            file=self.file_obj,
            original_file_name=file_name,
            file_name=generate_file_name(file_name),
            file_type=file_type,
            uploader=self.user,
            uploaded_at=timezone.now(),
        )

        obj.full_clean()
        obj.save()

        return obj
