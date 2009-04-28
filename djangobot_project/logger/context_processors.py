
from django.conf import settings

def logger(request):
    user_timezone = request.session.get("user_timezone", settings.TIME_ZONE)
    return {"user_timezone": user_timezone}
