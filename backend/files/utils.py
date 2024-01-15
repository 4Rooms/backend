import pathlib
from urllib.parse import urljoin, urlparse
from uuid import uuid4

from django.conf import settings


def generate_file_name(name, file_type=None):
    return f"{uuid4().hex}." + file_type or pathlib.Path(name).suffix


def get_upload_path(instance, filename):
    return f"uploads/{instance.file_name}"


def get_full_file_url(path: str) -> str:
    """Return full url of a file"""

    parsed = urlparse(settings.DJANGO_HOST)
    if parsed.hostname == "localhost":
        return urljoin(settings.DJANGO_HOST, path)

    if path.startswith("/media"):
        path = path[len("/media") :]
    return urljoin(f"{parsed.scheme}://files{parsed.hostname}", path)
