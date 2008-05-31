
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

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'logger.context_processors.logger',
)

INSTALLED_APPS = (
    # "django_evolution",
    
    "django.contrib.sessions",
    "django.contrib.humanize",
    
    "timezones",
    
    "bot",
    "logger",
)

SEARCH_INDEX_NAME = "logger_message"
