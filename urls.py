
from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^logger/", include("logger.urls")),
)

if settings.LOCAL_DEV:
    urlpatterns += patterns("django.views",
        url(r"^static/(?P<path>.*)", "static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
