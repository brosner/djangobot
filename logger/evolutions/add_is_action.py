
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField("Message", "is_action", models.BooleanField, initial=False)
]
