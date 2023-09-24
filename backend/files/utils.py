import pathlib
from uuid import uuid4


def generate_file_name(name):
    return f"{uuid4().hex}" + pathlib.Path(name).suffix


def get_upload_path(instance, filename):
    return f"uploads/{instance.file_name}"
