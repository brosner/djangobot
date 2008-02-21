
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list

from irc.views import *
from irc.models import Channel

urlpatterns = patterns("",
    url(r"^(?P<channel_name>[-\w]+)/$", channel_detail, name="channel_detail"),
    url(r"^$", object_list, {
        "queryset": Channel.objects.all(),
    }, name="channel_list"),
)
