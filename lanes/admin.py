from django.contrib import admin
from . import models


class LaneAdmin(admin.ModelAdmin):
    list_filter = ('cluster__name',)

admin.site.register(models.Lane, LaneAdmin)

admin.site.register(models.LaneReservation)

admin.site.register(models.LaneFullTimeValidator)
admin.site.register(models.LaneGivenHoursAndWeekdaysValidator)
admin.site.register(models.LaneTimeIntervalValidator)
admin.site.register(models.LaneNotWithinPeriodValidator)
admin.site.register(models.LaneMaxReservationsPerUserValidator)


class PeriodInline(admin.TabularInline):
    model = models.Period


class WithinPeriodValidatorAdmin(admin.ModelAdmin):
    inlines = [PeriodInline]


admin.site.register(models.LaneWithinPeriodValidator, WithinPeriodValidatorAdmin)
