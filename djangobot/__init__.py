
import os
import re
import time
import urllib
import urllib2
import Queue

import feedparser

from twisted.words.protocols import irc
from twisted.application import internet, service
from twisted.internet import protocol, reactor, task
from twisted.python import log

from django.conf import settings
from django.utils.encoding import force_unicode

from logger import models

activity_set = set()


class HTTPHeadRequest(urllib2.Request):

    def get_method(self):
        return "HEAD"


def log_irc_message(user, channel, message, is_action=False):
    """
    Logs this message to the database.
    """
    if not settings.BOT_LOGGING:
        return
    message = force_unicode(message, errors="replace")
    msg = models.Message(nickname=user.nickname, text=message,
                         is_action=is_action)
    msg.channel = channel.db_obj
    msg.save()


class User(object):
    """
    A single IRC user.
    """

    def __init__(self, nickname):
        self.nickname = nickname

    def msg(self, message):
        """
        Sends a message to the user.
        """
        log.msg("User.msg(nickname='%s', message='%s')" % (
                self.nickname, message))
        self.protocol.msg(self.nickname, message)


class ChannelPool(object):
    """
    A collection of IRC channels.
    """

    def __init__(self, channels=None):
        self.channels = {}
        if channels is not None:
            for channel in channels:
                self.add(channel)

    def __iter__(self):
        for channel in self.channels.values():
            yield channel

    def __getitem__(self, channel):
        return self.channels[channel.lower()]

    def add(self, channel):
        # perform a quick optimization to speed up lookups
        self.channels[channel.name] = channel

    def _all_joined(self):
        """
        Returns True if all channels in the pool have been joined. Otherwise,
        return False.
        """
        for channel in self.channels.values():
            if not channel.joined:
                return False
        return True
    all_joined = property(_all_joined)

    def msg(self, message):
        """
        Sends a message to all the channels in the pool.
        """
        for channel in self:
            channel.msg(message)


class Channel(object):
    """
    A single IRC channel.
    """

    def __init__(self, name, nickname, joined=False):
        self.name = name
        self.nickname = nickname
        self.joined = joined
        self.users = {}
        self.queue = Queue.Queue()
        self.db_obj, created = models.Channel.objects.get_or_create(name=self.name)

    def msg(self, message):
        # TODO: fix this by making sure nickname turns into a User object.

        class dumbHACK(object):
            nickname = self.nickname

        log_irc_message(dumbHACK(), self, message)
        log.msg("Channel.msg(channel='%s', message='%s')" % (
                self.name, message))
        self.protocol.msg(self.name, message)

    def add_user(self, user):
        user.protocol = self.protocol
        self.users[user.nickname] = user


class Message(object):
    """
    A single IRC message sent from a channel
    """

    def __init__(self, user, channel, message, is_action=False):
        self.user = user
        self.channel = channel
        self.message = message
        self.is_action = is_action

    def parse_as_command(self):
        try:
            cmd, params = self.message.split(" ", 1)
        except ValueError:
            cmd, params = self.message, ()
        else:
            params = [param for param in params.split(" ") if param]
        self.resolve_command(cmd)(*params)

    def resolve_command(self, cmd):
        try:
            cmd_func = getattr(self, "cmd_%s" % cmd)
        except AttributeError:
            return self.cmd_unknown
        else:
            return cmd_func

    def parse_as_normal(self):
        self.log()
        activity_set.add(self.user)
        if self.message.lower().startswith(
           self.channel.nickname.lower() + ":"):
            self.channel.msg("%s: i am a bot. brosner is my creator. " \
                "http://code.djangoproject.com/wiki/DjangoBot" % \
                self.user.nickname)
        # find any referenced tickets in this message
        # this requires the syntax #1000 to trigger.
        tickets = re.findall(r"(?:^|[\s(])#(\d+)\b", self.message)
        self.cmd_ticket(*tickets, **dict(in_channel=True))
        # find changesets. requires r1000 syntax.
        changesets = re.findall(r"\br(\d+)\b", self.message)
        self.cmd_changeset(*changesets, **dict(in_channel=True))

    def check_url(self, url):
        try:
            urllib2.urlopen(HTTPHeadRequest(url))
        except urllib2.HTTPError:
            return False
        else:
            return True

    def cmd_unknown(self, *params):
        self.user.msg("unknown command")
    cmd_unknown.usage = "is an unknown command."

    def cmd_help(self, *commands):
        if not commands:
            self.user.msg("available commands: who ticket changeset")
        else:
            for cmd in commands:
                method = self.resolve_command(cmd)
                if hasattr(method, "usage"):
                    self.user.msg("%s %s" % (cmd, method.usage))
                if hasattr(method, "help_text"):
                    self.user.msg(method.help_text)
    cmd_help.usage = "[command ...]"
    cmd_help.help_text = "Sends back help about the given command(s)."

    def cmd_ticket(self, *tickets, **kwargs):
        in_channel = kwargs.get("in_channel", False)
        if self.channel.name == "#django-hotclub":
            base_url = "http://code.google.com/p/django-hotclub/issues/detail?id=%s"
        else:
            base_url = "http://code.djangoproject.com/ticket/%s"
        for ticket in tickets:
            url = base_url % ticket
            if self.check_url(url):
                if in_channel:
                    self.channel.msg(url)
                else:
                    self.user.msg(url)
    cmd_ticket.usage = "<ticket> [<ticket> ...]"
    cmd_ticket.help_text = "Sends back Trac links to the given ticket(s)."

    def cmd_changeset(self, *changesets, **kwargs):
        in_channel = kwargs.get("in_channel", False)
        if self.channel.name == "#django-hotclub":
            base_url = "http://code.google.com/p/django-hotclub/source/detail?r=%s"
        else:
            base_url = "http://code.djangoproject.com/changeset/%s"
        for changeset in changesets:
            url = base_url % changeset
            if self.check_url(url):
                if in_channel:
                    self.channel.msg(url)
                else:
                    self.user.msg(url)
    cmd_changeset.usage = "<changeset> [<changeset> ...]"
    cmd_changeset.help_text = "Sends back Trac links to the given" + \
                              " changeset(s)."

    def cmd_who(self, *nicknames):
        for nickname in [n.strip() for n in nicknames]:
            try:
                dp = "http://djangopeople.net/api/irc_lookup/%s/" % nickname
                u = urllib2.urlopen(dp)
            except urllib2.HTTPError:
                self.user.msg("something went wrong!")
            else:
                response = u.read()
                if response == "no match":
                    self.user.msg("%s was not found." % nickname)
                else:
                    self.user.msg("%s is %s" % (nickname, response))
    cmd_who.usage = "<nickname> [<nickname> ...]"
    cmd_who.help_text = "Sends back the real name, location and URL for" + \
                        " the nickname if the person is registered on" + \
                        " djangopeople.net."

    def log(self):
        """
        Logs this message to the database.
        """
        log_irc_message(self.user, self.channel,
                        self.message, is_action=self.is_action)


class DjangoBotProtocol(irc.IRCClient):

    # wait two seconds between sending messages to channels and users.
    lineRate = 2

    def connectionMade(self):
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)

    def trac_updates(self, channel):
        try:
            # dont block here so the bot can continue to work.
            entries = channel.queue.get(block=False)
        except Queue.Empty:
            pass
        else:
            for entry in reversed(entries):
                channel.msg(entry)

    def signedOn(self):
        """
        Join the channel after sign on.
        """
        for channel in self.factory.channels:
            # this seems a bit hackish. look into this later when it comes to
            # mulitple nicknames. it probably needs to be escalated to a higher
            # level and multiple threads for each nick.
            channel.protocol = self
            # don't join the nickname channel
            if channel.name == self.nickname:
                continue
            self.join(channel.name)

    def joined(self, channel):
        """
        Once the bot has signed into the channel begin the trac updates.
        """
        c = self.factory.channels[channel]
        c.joined = True
    
    def userJoined(self, user, channel):
        pass
    
    def userLeft(self, user, channel):
        pass
    
    def privmsg(self, user, channel, message, is_action=False):
        if self.factory.channels.all_joined:
            try:
                c = self.factory.channels[channel]
            except KeyError:
                return
            # TODO: the channel list of users should be prefilled by this point
            # so it is a quick lookup.
            nickname = user.split("!", 1)[0]
            try:
                u = c.users[nickname]
            except KeyError:
                u = User(nickname)
                c.add_user(u)
            msg = Message(u, c, message, is_action=is_action)
            if channel.lower() == self.nickname.lower():
                msg.parse_as_command()
            else:
                msg.parse_as_normal()

    def action(self, user, channel, message):
        self.privmsg(user, channel, message, is_action=True)


class DjangoBotService(service.Service):

    def __init__(self, channels, nickname, password):
        self.channels = channels
        self.nickname = nickname
        self.password = password

    def getFactory(self):
        factory = protocol.ReconnectingClientFactory()
        factory.protocol = DjangoBotProtocol
        factory.channels = self.channels
        factory.nickname, factory.password = self.nickname, self.password
        # create a channel for private messages
        factory.channels.add(Channel(self.nickname,
                                     self.nickname, joined=True))
        return factory


class TracFeedFetcher(object):
    opts = {
        "ticket": True,
        "changeset": True,
    }

    def __init__(self, trac_url, interval, channels, **options):
        self.trac_url = trac_url
        self.interval = interval
        self.channels = channels
        self.opts.update(options)
        self.seen_entries = {}
        self.first_flag = True

    def get_feed_url(self):
        url = "%s/timeline/?format=rss&max=50&daysback=1"
        if self.opts["ticket"]:
            url += "&ticket=on"
        if self.opts["changeset"]:
            url += "&changeset=on"
        return url % self.trac_url

    def __call__(self):
        self.start()

    def start(self):
        self._loop = task.LoopingCall(self.fetch)
        self._loop.start(self.interval, now=True).addErrback(self._failed)

    def _failed(self, why):
        self._loop.running = False
        log.err(why)

    def stop(self):
        if self._loop.running:
            self._loop.stop()

    def fetch(self):
        feed = feedparser.parse(self.get_feed_url())
        entries = []
        for entry in feed.entries:
            if entry.id not in self.seen_entries:
                # Twisted won't let me write unicode objects to the socket, so
                # here I need to encode the data in UTF-8.
                msg = "%s (%s)" % (entry.title, entry.link)
                entries.append(msg.encode("UTF-8"))
            self.seen_entries[entry.id] = True
        if self.first_flag:
            self.first_flag = False
            return
        for channel in self.channels:
            # limit the list entries to no more than 5
            channel.queue.put(entries[:5])


class TracMonitorService(service.Service):

    def __init__(self, trac_url, interval, channels):
        self.fetcher = TracFeedFetcher(trac_url, interval, channels)

    def startService(self):
        reactor.callInThread(self.fetcher)
        service.Service.startService(self)

    def stopService(self):
        self.fetcher.stop()
        service.Service.stopService(self)


class BadRequest(Exception):
    pass


class DjangoPeopleMonitor(object):

    def __init__(self):
        self.interval = 60

    def __call__(self):
        self.run()

    def run(self):
        self._loop = task.LoopingCall(self.execute)
        self._loop.start(self.interval, now=True).addErrback(self._failed)

    def _failed(self, why):
        self._loop.running = False
        log.err(why)

    def stop(self):
        if self._loop.running:
            self._loop.stop()

    def execute(self):
        for user in activity_set:
            try:
                self.send(user)
            except BadRequest:
                pass
        activity_set.clear()
    
    def send(self, user):
        try:
            dp = "http://djangopeople.net/api/irc_spotted/%s/"
            u = urllib2.urlopen(dp % user.nickname,
                    urllib.urlencode({"sekrit": settings.DJANGOPEOPLE_SEKRIT}))
        except (urllib2.HTTPError, urllib2.URLError):
            raise BadRequest
        else:
            ret = u.read()
        if ret == "FIRST_TIME_SEEN":
            user.msg("You're now being tracked on http://djangopeople.net/" + \
                     "irc/active/ - log in to djangopeople.net and edit " + \
                     "your privacy preferences if you'd rather not be")
        log.msg("%s - %s" % (user.nickname, ret))


class DjangoPeopleMonitorService(service.Service):
    def __init__(self):
        self.monitor = DjangoPeopleMonitor()
    
    def startService(self):
        reactor.callInThread(self.monitor)
        service.Service.startService(self)
    
    def stopService(self):
        self.monitor.stop()
        service.Service.stopService(self)
