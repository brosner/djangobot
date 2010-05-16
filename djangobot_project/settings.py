
import os

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

LOCAL_DEV = False
PAGINATE_BY = 100
TIME_ZONE = "UTC"

BOT_IRC_SERVER = "irc.freenode.org"
BOT_IRC_PORT = 6667
BOT_NICKNAME = ""
BOT_PASSWORD = ""
BOT_CHANNELS = []
BOT_LOGGING = False

ROOT_URLCONF = "djangobot_project.urls"

INTERNAL_IPS = [
    "127.0.0.1",
]

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "static")
MEDIA_URL = "/static/"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
]

MIDDLEWARE_CLASSES = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "logger.context_processors.logger",
]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.humanize",
    "timezones",
    "debug_toolbar",
    "logger",
]

SEARCH_INDEX_NAME = "logger_message"

try:
    from local_settings import *
except ImportError:
    pass
