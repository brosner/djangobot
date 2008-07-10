#!/usr/bin/env python

from django.core.management import setup_environ
import settings as settings_mod

setup_environ(settings_mod)

from twisted.words.protocols import irc
from twisted.application import internet, service
from twisted.internet import protocol, reactor, task
from twisted.python import log

from django.conf import settings
from djangobot.bot import DjangoBotService, ChannelPool, Channel
from djangobot.bot import DjangoPeopleMonitorService

application = service.Application("djangobot")
serv = service.MultiService()

nickname = settings.BOT_NICKNAME

channels = ChannelPool()
for name in settings.BOT_CHANNELS:
    channels.add(Channel(name, nickname))

dbs = DjangoBotService(channels, nickname, settings.BOT_PASSWORD)

internet.TCPClient(
    settings.BOT_IRC_SERVER, settings.BOT_IRC_PORT,
    dbs.getFactory(),
).setServiceParent(serv)

if settings.BOT_DJANGOPEOPLE:
    DjangoPeopleMonitorService().setServiceParent(serv)

serv.setServiceParent(application)
