from django.contrib import admin
from . import models


class LaneAdmin(admin.ModelAdmin):
    list_filter = ('cluster__name',)

admin.site.register(models.Lane, LaneAdmin)

admin.site.register(models.LaneReservation)

admin.site.register(models.FullTimeValidator)
admin.site.register(models.GivenHoursAndWeekdaysValidator)
admin.site.register(models.TimeIntervalValidator)
admin.site.register(models.NotWithinPeriodValidator)
admin.site.register(models.MaxReservationsPerUserValidator)


class PeriodInline(admin.TabularInline):
    model = models.Period


class WithinPeriodValidatorAdmin(admin.ModelAdmin):
    inlines = [PeriodInline]


admin.site.register(models.WithinPeriodValidator, WithinPeriodValidatorAdmin)
