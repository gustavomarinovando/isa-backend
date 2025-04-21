from django.contrib import admin
from .models import AcademicObjective, SGCObjective, Month, KPI

admin.site.register(AcademicObjective)
admin.site.register(SGCObjective)
admin.site.register(Month)
admin.site.register(KPI)