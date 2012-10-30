from django.contrib import admin
from models import Constraint


class ConstraintAdmin(admin.ModelAdmin):
    pass

admin.site.register(Constraint, ConstraintAdmin)
