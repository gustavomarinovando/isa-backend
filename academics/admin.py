from django.contrib import admin
from .models import AcademicYear, Trimestre, Periodo, GradeLevel, Paralelo, Subject
# Register your models here.

admin.site.register(AcademicYear)
admin.site.register(Trimestre)
admin.site.register(Periodo)
admin.site.register(GradeLevel)
admin.site.register(Paralelo)
admin.site.register(Subject)