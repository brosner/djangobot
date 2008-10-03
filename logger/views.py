
import datetime

from django.conf import settings
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.date_based import archive_day
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, InvalidPage

from logger.models import Channel, Message

def smart_page_range(paginator):
    # TODO: make this smarter :P
    page_range = [1, 2, 3, 4, "..."]
    page_range.extend(range(paginator.num_pages - 3, paginator.num_pages + 1))
    return page_range

def channel_search(request, channel_name):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    query = request.GET.get("q", "")
    paginator = Paginator(Message.search.query(query).filter(channel_id=channel.pk).order_by("logged"), settings.PAGINATE_BY)
    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:
        return HttpResponseBadRequest()
    try:
        page = paginator.page(page_number)
    except InvalidPage:
        raise Http404
    context = {
        "channel": channel,
        "channel_name": channel_name, # used for {% url %}
        "date": datetime.datetime.today(),
        "page": page,
        "page_range": smart_page_range(paginator),
        "paginator": paginator,
        "is_paginated": paginator.count >= settings.PAGINATE_BY,
        "messages": page.object_list,
    }
    return render_to_response("logger/channel_detail.html", 
        context, context_instance=RequestContext(request))

def channel_detail(request, channel_name):
    """
    Latest 100 messages of the channel.
    """
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    return render_to_response("logger/channel_detail.html", {
        "channel": channel,
        "channel_name": channel_name,
        "date": datetime.date.today(), # @@@: bad assumption, fixme later.
        "messages": reversed(channel.message_set.order_by("-logged")[:100]),
    }, context_instance=RequestContext(request))
channel_detail = never_cache(channel_detail)

def channel_detail_day(request, channel_name, year, month, day, page=None):
    channel = get_object_or_404(Channel, name="#%s" % channel_name)
    ctx = {}
    date = datetime.date(*map(int, (year, month, day)))
    # check if the date is today, if True then dont allow caching.
    if date == datetime.date.today():
        ctx.update({"today": True})
    paginator = Paginator(channel.message_set.filter(
        logged__range=(date, date + datetime.timedelta(days=1)),
    ).order_by("logged"), settings.PAGINATE_BY)
    if page is None:
        page_number = paginator.num_pages
    else:
        try:
            page_number = int(page)
        except ValueError:
            return HttpResponseBadRequest()
    try:
        page = paginator.page(page_number)
    except InvalidPage:
        raise Http404
    return render_to_response("logger/channel_detail_day.html", dict(ctx, **{
        "channel": channel,
        "channel_name": channel_name, # used for {% url %}
        "date": date,
        "paginator": paginator,
        "is_paginated": paginator.count >= settings.PAGINATE_BY,
        "page_number": page_number,
        "page": page,
        "messages": page.object_list,
    }), context_instance=RequestContext(request))
