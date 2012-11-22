from django.contrib import admin
from models import Lane, LaneReservation, LaneFullTimeValidator


class LaneAdmin(admin.ModelAdmin):
    list_filter = ('cluster__name',)

admin.site.register(Lane, LaneAdmin)


class LaneReservationAdmin(admin.ModelAdmin):
    pass
admin.site.register(LaneReservation, LaneReservationAdmin)
admin.site.register(LaneFullTimeValidator)
