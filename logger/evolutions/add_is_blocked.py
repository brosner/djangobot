
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField("Message", "is_blocked", models.BooleanField, initial=False)
]
