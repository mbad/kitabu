from django.contrib import admin
from models import Lane, LaneReservation

class LaneAdmin(admin.ModelAdmin):
    pass
admin.site.register(Lane, LaneAdmin)


class LaneReservationAdmin(admin.ModelAdmin):
    pass
admin.site.register(LaneReservation, LaneReservationAdmin)