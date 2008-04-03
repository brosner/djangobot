#!/usr/bin/env python

import os
import time

from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read("djangobot.ini")

from django.conf import settings

settings.configure(**{
    "DATABASE_ENGINE": config.get("db", "engine"),
    "DATABASE_NAME": config.get("db", "name"),
    "TIME_ZONE": "UTC",
    "INSTALLED_APPS": (
        "irc",
    ),
})

os.environ["TZ"] = settings.TIME_ZONE
time.tzset()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line()
