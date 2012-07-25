from django.db import models
from reservable import ExclusiveReservable

from deferred.deferred import DeferredField, DeferredForeignKey, DeferredModel

class Reservable(ExclusiveReservable):
    class Meta:
        app_label = 'reservations'
    name = models.TextField(null=True, blank=True)

class Reservation(models.Model):
    reservable = models.ForeignKey('Reservable')
    start = models.DateTimeField()
    end = models.DateTimeField()

class SomeDeferredExample(DeferredModel):
    a = DeferredField(models.TextField())
    b = DeferredField(models.TextField())
    c = DeferredField(models.TextField())

    class Meta:
        abstract = True


class SomeInheritedDeferredExample(SomeDeferredExample):
    a = DeferredField(models.BooleanField())
    d = models.TextField()

    class Meta:
        abstract = True
        
class Example(SomeInheritedDeferredExample.settle( c = models.BigIntegerField() )):
    pass
