from django.db import models
from django.db.models.sql.aggregates import Aggregate


class FloorPercentage(Aggregate):
    sql_function = "FLOOR"
    sql_template = "%(function)s((COUNT(%(field)s) / %(total_count)d.0) * 100)"


class Percentage(models.Aggregate):
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = FloorPercentage(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate