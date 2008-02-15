
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from irc.models import Channel

def channel_detail(request, channel_name):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    return render_to_response("irc/channel_detail.html", {
        "channel": channel,
        "messages": channel.message_set.all()[:100],
    }, context_instance=RequestContext(request))
