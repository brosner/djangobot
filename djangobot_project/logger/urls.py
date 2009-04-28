
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list

from logger.views import *
from logger.models import Channel

urlpatterns = patterns("",
    url(r"^search/(?P<channel_name>[-\w]+)/$", channel_search, name="channel_search"),
    url(r"^(?P<channel_name>[-\w]+)/$", channel_detail, name="channel_detail"),
    url(r"^(?P<channel_name>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$", 
        channel_detail_day, name="channel_detail_day"),
    url(r"^(?P<channel_name>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<page>\d+)/$",
        channel_detail_day, name="channel_detail_day_page"),
    url(r"^$", object_list, {
        "queryset": Channel.objects.all(),
    }, name="channel_list"),
)
