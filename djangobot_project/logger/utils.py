from django.db import models
from logger.sql import Percentage


def top_talkers(channel=None, count=10):
    """
    Returns a queryset of the top talkers in all channels.
    """
    from logger.models import Message
    queryset = Message.objects.all()
    if channel is not None:
        queryset = queryset.filter(channel=channel)
        total_count = channel.message_set.count()
    else:
        total_count = Message.objects.count()
    queryset = queryset.values(
       "nickname",
    ).annotate(
       message_count = models.Count("id"),
       percentage = Percentage("id", total_count=total_count),
    ).order_by("-message_count")
    return queryset[0:count]
