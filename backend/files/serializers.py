from rest_framework import serializers

from .models import File


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("url", "file_name", "file_type", "uploader", "uploaded_at")
