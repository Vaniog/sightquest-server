import os
from .routing import application  # Не удалять, это нужно, чтобы Django увидел application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
