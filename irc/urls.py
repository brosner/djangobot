
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list

from irc.views import *
from irc.models import Channel

urlpatterns = patterns("",
    url(r"^(?P<channel_name>[-\w]+)/$", channel_detail, name="channel_detail"),
    url(r"^(?P<channel_name>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$", 
        channel_detail_day, name="channel_detail_day"),
    url(r"^$", object_list, {
        "queryset": Channel.objects.all(),
    }, name="channel_list"),
)
