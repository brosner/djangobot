
from datetime import datetime

from django.db import models

class Channel(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    
    class Admin:
        pass
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        channel_name = self.name[0] == "#" and self.name[1:] or self.name
        return ("channel_detail", (), {"channel_name": channel_name})
    get_absolute_url = models.permalink(get_absolute_url)

class Message(models.Model):
    channel = models.ForeignKey(Channel, db_index=True)
    nickname = models.CharField(max_length=19, db_index=True)
    text = models.TextField()
    is_action = models.BooleanField(default=False)
    logged = models.DateTimeField(default=datetime.now)
    
    class Admin:
        list_display = ("channel", "nickname", "text", "logged")
        list_filter = ("channel", "logged")
    
    class Meta:
        ordering = ("logged",)
    
    def __unicode__(self):
        return u"<%s> %s [%s]" % (self.nickname, self.text, self.logged)
