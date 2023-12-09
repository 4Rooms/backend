from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File
from .serializers import FileUploadSerializer
from .services.file_upload import FileUploadService


class FileUploadView(APIView):
    @extend_schema(
        tags=["Files"],
        operation_id="upload_file",
        request={
            "multipart/form-data": {"type": "object", "properties": {"file": {"type": "string", "format": "binary"}}}
        },
        responses={
            201: FileUploadSerializer,
            400: "File size is too large.",
        },
    )
    def post(self, request):
        service = FileUploadService(user=request.user, file_obj=request.FILES["file"])
        file = service.create()

        return Response(data=FileUploadSerializer(file).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return File.objects.all()
