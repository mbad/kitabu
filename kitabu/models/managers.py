from django.db import models
from django.db.models import Q
from datetime import datetime


class ApprovableReservationsManager(models.Manager):
    def get_query_set(self):
        q = Q(approved=True) | Q(valid_until__gt=datetime.utcnow())
        return super(ApprovableReservationsManager, self).get_query_set().filter(q)

    def with_invalid(self):
        return super(ApprovableReservationsManager, self).get_query_set()
