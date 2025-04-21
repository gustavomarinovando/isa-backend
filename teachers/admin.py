from django.contrib import admin
from .models import Teacher, PeriodProgress, TopicCompletion

admin.site.register(Teacher)
admin.site.register(PeriodProgress)
admin.site.register(TopicCompletion)