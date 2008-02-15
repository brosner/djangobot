
from django.conf.urls.defaults import *

from irc.views import *

urlpatterns = patterns("",
    url(r"^(?P<channel_name>[-\w]+)/$", channel_detail),
)
