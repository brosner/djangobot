
from datetime import datetime

from django.db import models

class Channel(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    
    class Admin:
        pass
    
    def __unicode__(self):
        return self.name

class Message(models.Model):
    channel = models.ForeignKey(Channel, db_index=True)
    nickname = models.CharField(max_length=19, db_index=True)
    text = models.TextField()
    logged = models.DateTimeField(default=datetime.now)
    
    class Admin:
        list_display = ("channel", "nickname", "text", "logged")
        list_filter = ("channel", "logged")
    
    class Meta:
        ordering = ("logged",)
    
    def __unicode__(self):
        return u"<%s> %s [%s]" % (self.nickname, self.text, self.logged)
