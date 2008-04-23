
from django.db import models
from django.db.models.query import QuerySet

class GroupByQuerySet(QuerySet):
    """
    A QuerySet that taps into TODO functionality of a QuerySet in
    queryset-refactor. This is to be used ONLY with the very limited use-case
    for this logger.
    """
    def group_by(self, *fields):
        obj = self._clone()
        obj.query.group_by.extend(fields)
        return obj

class ChannelManager(models.Manager):    
    def top_talkers(self, channel, count=10):
        """
        Returns a list of dicts containing nickname and message counts for the
        top talkers in the given channel.
        """
        queryset = channel.message_set.all()
        queryset = queryset.extra(select={
            "message_count": "COUNT(*)"
        }).group_by("nickname").values("nickname", "message_count").order_by("-message_count")
        return queryset[0:count]

class MessageManager(models.Manager):
    def get_query_set(self):
        return GroupByQuerySet(self.model)
