
from django.db import models
from logger.utils import top_talkers


class ChannelManager(models.Manager):    
    def top_talkers(self, channel, **kwargs):
        kwargs.update({"channel": channel})
        return top_talkers(**kwargs)