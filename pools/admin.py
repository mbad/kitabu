from django.contrib import admin
from models import Pool


class PoolAdmin(admin.ModelAdmin):
    pass


admin.site.register(Pool, PoolAdmin)
