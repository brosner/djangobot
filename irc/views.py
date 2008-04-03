import datetime
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.date_based import archive_day

from irc.models import Channel

def channel_detail(request, channel_name):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    return render_to_response("irc/channel_detail.html", {
        "channel": channel,
        "date": datetime.datetime.today(),
        "messages": reversed(channel.message_set.order_by("-logged")[:100]),
    }, context_instance=RequestContext(request))
channel_detail = never_cache(channel_detail)

def channel_detail_day(request, channel_name, year, month, day):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    date = datetime.date(*map(int, (year, month, day)))
    return render_to_response("irc/channel_detail_day.html", {
        "channel": channel,
        "date": date,
        "messages": channel.message_set.filter(
            logged__range=(date, date + datetime.timedelta(days=1)),
        ).order_by("logged"),
    }, context_instance=RequestContext(request))
