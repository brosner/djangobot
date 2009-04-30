
from datetime import datetime

from django.db import models
from django.conf import settings

from logger.managers import ChannelManager

class Channel(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    
    objects = ChannelManager()
    
    class Meta:
        db_table = "irc_channel" # for backward compatibility
    
    class Admin:
        pass
    
    def __unicode__(self):
        return self.name
    
    def clean_name(self):
        return self.name[0] == "#" and self.name[1:] or self.name
    
    def top_talkers(self, count=10):
        return Channel.objects.top_talkers(self, count)
    
    def get_absolute_url(self):
        return ("channel_detail", (), {"channel_name": self.clean_name()})
    get_absolute_url = models.permalink(get_absolute_url)

class Message(models.Model):
    channel = models.ForeignKey(Channel, db_index=True)
    nickname = models.CharField(max_length=19, db_index=True)
    text = models.TextField()
    is_action = models.BooleanField(default=False)
    logged = models.DateTimeField(default=datetime.now, db_index=True)
    is_blocked = models.BooleanField(default=False)
    
    class Admin:
        list_display = ("channel", "nickname", "text", "logged")
        list_filter = ("channel", "logged")
    
    class Meta:
        db_table = "irc_message" # for backward compatibility
        ordering = ("logged",)
    
    def __unicode__(self):
        return u"<%s> %s [%s]" % (self.nickname, self.text, self.logged)

def top_talkers(count=10):
    """
    Returns a queryset of the top talkers in all channels.
    """
    queryset = Message.objects.all()
    queryset = queryset.extra(select={
        "message_count": "COUNT(*)",
        "percentage": "FLOOR((COUNT(*) / %d.0) * 100)" % Message.objects.count(),
    }).group_by("nickname").values(
        "nickname", "message_count", "percentage",
    ).order_by("-message_count")
    return queryset[0:count]
