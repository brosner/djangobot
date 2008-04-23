
import os

from django.conf.global_settings import *

LOCAL_DEV = False
PAGINATE_BY = 100
TIME_ZONE = "UTC"

BOT_IRC_SERVER = "irc.freenode.org"
BOT_IRC_PORT = 6667
BOT_NICKNAME = ""
BOT_PASSWORD = ""
BOT_CHANNELS = ()
BOT_LOGGING = False

ROOT_URLCONF = "djangobot.urls"

MEDIA_URL = "/static/"

TEMPLATE_DIRS = (
    #
    # IMPORT NOTE:
    # you need to specify this in your own settings.py.
    #
)

INSTALLED_APPS = (
    # "django_evolution",
    
    "django.contrib.sessions",
    "django.contrib.humanize",
    
    "bot",
    "logger",
)

SEARCH_INDEX_NAME = "logger_message"
