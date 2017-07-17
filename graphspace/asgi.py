import os
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphspace.settings.local")

channel_layer = get_channel_layer()

from graphspace.database import *
from django.conf import settings
settings.db = Database()

from applications.notifications.consumer import *

# Start owner notification consumer
ocon = Consumer("owner")
ocon.start()

# Start group notification consumer
gcon = Consumer("group")
gcon.start()
