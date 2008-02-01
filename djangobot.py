
import re
import sys
import time
import urllib2

from twisted.python import log
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

class MessageLogger(object):
    def __init__(self, stream):
        self.stream = stream
    
    def log(self, message):
        ts = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.stream.write("%s %s\n" % (ts, message))
        self.stream.flush()
    
    def close(self):
        self.stream.close()

class TracTicketBot(irc.IRCClient):
    """
    An IRC bot that logs each message in an given channel.
    """
    
    nickname = "DjangoBot"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(sys.stdout)
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))
    
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()
    
    def signedOn(self):
        self.join(self.factory.channel)
    
    def joined(self, channel):
        self.logger.log("[joined %s]" % channel)
    
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
        tickets = re.findall(r".?\#(\d+)", message)
        for ticket in tickets:
            url = "http://code.djangoproject.com/ticket/%s" % ticket
            if self.get_url(url):
                self.msg(channel, url)
        # find changesets. requires r1000 syntax.
        changesets = re.findall(r".?r(\d+)", message)
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
    
    def action(self, user, channel, message):
        pass

class IRCFactory(protocol.ClientFactory):
    protocol = TracTicketBot
    
    def __init__(self, channel):
        self.channel = channel
    
    def clientConnectionLost(self, connector, reason):
        """
        If we get disconnected, reconnect to server.
        """
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        """
        """
        print "connection failed:", reason
        reactor.stop()

def main():
    log.startLogging(open("/home/djangobot/djangobot.log"))
    f = IRCFactory(sys.argv[1])
    reactor.connectTCP("irc.freenode.net", 6667, f)
    reactor.run()

if __name__ == "__main__":
    main()
