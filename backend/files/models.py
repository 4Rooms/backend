from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from .utils import get_upload_path


class File(models.Model):
    file = models.FileField(upload_to=get_upload_path, blank=True, null=True)

    original_file_name = models.TextField()

    file_name = models.CharField(max_length=255, unique=True)
    file_type = models.CharField(max_length=255)

    uploader = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(blank=True, null=True)

    @property
    def url(self):
        return f"{settings.DJANGO_HOST}{self.file.url}"
