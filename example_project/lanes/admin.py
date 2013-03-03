from django.contrib import admin
from . import models


class LaneAdmin(admin.ModelAdmin):
    list_filter = ('cluster__name',)

admin.site.register(models.Lane, LaneAdmin)

admin.site.register(models.LaneReservation)

admin.site.register(models.LFullTimeValidator)
admin.site.register(models.LTimeIntervalValidator)
admin.site.register(models.LNotWithinPeriodValidator)
admin.site.register(models.LMaxReservationsPerUserValidator)


class PeriodInline(admin.TabularInline):
    model = models.Period


class WithinPeriodValidatorAdmin(admin.ModelAdmin):
    inlines = [PeriodInline]


admin.site.register(models.LWithinPeriodValidator, WithinPeriodValidatorAdmin)
