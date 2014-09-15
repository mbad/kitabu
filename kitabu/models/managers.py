from django.db import models
from django.db.models import Q
from django.utils import timezone


class ApprovableReservationsManager(models.Manager):
    def get_query_set(self):
        q = Q(approved=True) | Q(valid_until__gt=timezone.now())
        return super(ApprovableReservationsManager, self).get_query_set().filter(q)

    def with_invalid(self):
        return super(ApprovableReservationsManager, self).get_query_set()
