
import re
import urllib2

from twisted.words.protocols import irc
from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer

class DjangoBotProtocol(irc.IRCClient):
    def connectionMade(self):
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
    
    def signedOn(self):
        """
        Join the channel after sign on.
        """
        self.join(self.factory.channel)
    
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
    
    def getFactory(self):
        factory = protocol.ReconnectingClientFactory()
        factory.protocol = DjangoBotProtocol
        factory.channel = self.channel
        factory.nickname, factory.password = self.nickname, self.password
        return factory

application = service.Application("djangobot")
dbs = DjangoBotService("django", "DjangoBot")
internet.TCPClient(
    "irc.freenode.org", 6667, dbs.getFactory(),
).setServiceParent(service.IServiceCollection(application))
