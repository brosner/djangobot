
from django.db import models
from django.db.models.sql.aggregates import Aggregate


class FloorPercentage(Aggregate):
    sql_function = "FLOOR"
    sql_template = "%(function)s((COUNT(%(field)s) / %(total_count)d.0) * 100)"


class Percentage(models.Aggregate):
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = FloorPercentage(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate


class ChannelManager(models.Manager):    
    def top_talkers(self, channel, count=10):
        """
        Returns a list of dicts containing nickname and message counts for the
        top talkers in the given channel.
        """
        queryset = channel.message_set.all()
        queryset = queryset.values(
           "nickname",
        ).annotate(
           message_count = models.Count("id"),
           percentage = Percentage("id", total_count=channel.message_set.count()),
        ).order_by("-message_count")
        return queryset[0:count]
        