#!/usr/bin/env python

config = SafeConfigParser()
config.read("djangobot.ini")

from django.conf import settings

settings.configure(**{
    "DATABASE_ENGINE": config.get("db", "engine"),
    "DATABASE_NAME": config.get("db", "name"),
    "INSTALLED_APPS": (
        "irc",
    ),
})

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line()
