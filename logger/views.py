
import datetime

from django.conf import settings
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.date_based import archive_day
from django.http import Http404, HttpResponseBadRequest
from django.core.paginator import Paginator, QuerySetPaginator, InvalidPage

from logger.models import Channel, Message

def get_messages(channel, query=""):
    if query:
        return Message.search.query(query)
    return channel.message_set.all()

def channel_detail(request, channel_name):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    query = request.GET.get("q", "")
    paginator = QuerySetPaginator(get_messages(channel, query), settings.PAGINATE_BY)
    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:
        return HttpResponseBadRequest()
    try:
        page = paginator.page(page_number)
    except InvalidPage:
        raise Http404
    context = {
        "query": query,
        "channel": channel,
        "date": datetime.datetime.today(),
        "page": page,
        "paginator": paginator,
        "is_paginated": paginator.count >= settings.PAGINATE_BY,
        "messages": reversed(page.object_list.order_by("-logged")),
    }
    return render_to_response("logger/channel_detail.html", 
        context, context_instance=RequestContext(request))
channel_detail = never_cache(channel_detail)

def channel_detail_day(request, channel_name, year, month, day):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    date = datetime.date(*map(int, (year, month, day)))
    messages = get_messages(channel, request.GET.get("q", ""))
    return render_to_response("logger/channel_detail_day.html", {
        "channel": channel,
        "date": date,
        "messages": messages.filter(
            logged__range=(date, date + datetime.timedelta(days=1)),
        ).order_by("logged"),
    }, context_instance=RequestContext(request))
