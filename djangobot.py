
import re
import time
import urllib2
import Queue

import feedparser

from twisted.words.protocols import irc
from twisted.application import internet, service
from twisted.internet import protocol, reactor, task

queue = Queue.Queue()
signed_on = False

class DjangoBotProtocol(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
    
    def trac_updates(self, channel):
        try:
            # dont block here so the bot can continue to work.
            entries = queue.get(block=False)
        except Queue.Empty:
            pass
        else:
            for entry in entries:
                self.msg(channel, entry)
    
    def signedOn(self):
        """
        Join the channel after sign on.
        """
        self.join(self.factory.channel)
    
    def joined(self, channel):
        """
        Once the bot has signed into the channel begin the trac updates.
        """
        task.LoopingCall(self.trac_updates, channel).start(15)
    
    def privmsg(self, user, channel, message):
        user = user.split("!", 1)[0]
        if channel == self.nickname:
            try:
                cmd, params = message.split(" ", 1)
            except ValueError:
                # no params
                cmd = message
            if cmd == "who":
                try:
                    u = urllib2.urlopen("http://djangopeople.net/api/irc_lookup/%s/" % params.strip())
                except http.HTTPError:
                    self.msg(user, "something went wrong!")
                else:
                    self.msg(user, u.read())
            return
        if message.startswith(self.nickname + ":"):
            self.msg(channel, "%s: i am a bot. brosner is my creator." % user)
        # find any referenced tickets in this message
        # this requires the syntax #1000 to trigger.
        tickets = re.findall(r"(?:^|[\s(])#(\d+)\b", message)
        for ticket in tickets:
            url = "http://code.djangoproject.com/ticket/%s" % ticket
            if self.get_url(url):
                self.msg(channel, url)
        # find changesets. requires r1000 syntax.
        changesets = re.findall(r"\br(\d+)\b", message)
        for changeset in changesets:
            url = "http://code.djangoproject.com/changeset/%s" % changeset
            if self.get_url(url):
                self.msg(channel, url)
    
    def get_url(self, url):
        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError:
            return False
        else:
            return True

class DjangoBotService(service.Service):
    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname
        self.password = None
    
    def getFactory(self):
        factory = protocol.ReconnectingClientFactory()
        factory.protocol = DjangoBotProtocol
        factory.channel = self.channel
        factory.nickname, factory.password = self.nickname, self.password
        return factory

application = service.Application("djangobot")
serv = service.MultiService()

dbs = DjangoBotService("django", "DjangoBot")
internet.TCPClient(
    "irc.freenode.org", 6667, dbs.getFactory(),
).setServiceParent(serv)

class TracFeedFetcher(object):
    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.seen_entries = {}
    
    def __call__(self):
        self.fetch()
    
    def fetch(self):
        feed = feedparser.parse(self.feed_url)
        entries = []
        for entry in feed.entries:
            if entry.id not in self.seen_entries:
                # Twisted won't let me write unicode objects to the socket, so
                # here I need to encode the data in ascii replacing stuff that
                # won't work. (TODO: look into this more). Note, that I am
                # explicitly converting the data to a bytestring when adding
                # to the entries list.
                msg = "%s (%s)" % (entry.title.encode("ascii", "replace"), entry.link)
                entries.append(str(msg))
            self.seen_entries[entry.id] = True
        queue.put(entries)

# Keep this off until I get a configuration file working correctly.
if False:
    internet.TimerService(
        30, TracFeedFetcher("http://code.djangoproject.com/timeline?ticket=on&changeset=on&max=10&daysback=1&format=rss")
    ).setServiceParent(serv)

serv.setServiceParent(application)
