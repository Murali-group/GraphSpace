import os
import django
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphspace.settings.production")
django.setup()
channel_layer = get_channel_layer()

from graphspace.database import *
from django.conf import settings
settings.db = Database()