from django.db import models


class Universal(models.Manager):
    def get_query_set(self):
        return super(Universal, self).get_query_set().filter(apply_to_all=True)
