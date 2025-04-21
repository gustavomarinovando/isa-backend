from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from academics.models import AcademicYear, Periodo, GradeLevel, Paralelo, Subject


class Teacher(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True) # Allow null/blank initially
    google_sheet_url = models.URLField(unique=True, max_length=500) # Ensure length is sufficient
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['full_name']


class PeriodProgress(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='period_progress')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='period_progress') # NEW FK
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, related_name='period_progress') # Changed to FK
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='progress_records') # Changed to FK
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name='period_progress') # Changed to FK
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='period_progress_records') # Optional FK
    progress_percentage = models.FloatField()
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
         # Access related fields correctly
        return f"{self.teacher.full_name} - {self.grade_level.code} - P{self.periodo.number} - {self.paralelo.code}: {self.progress_percentage}% ({self.academic_year.year})"

    class Meta:
        # Update unique_together for ForeignKeys
        unique_together = ('teacher', 'academic_year', 'grade_level', 'periodo', 'paralelo')
        ordering = ['teacher', 'academic_year', 'grade_level', 'periodo__number', 'paralelo'] # Order by periodo number
        verbose_name_plural = "Period Progress Records"

class TopicCompletion(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='topic_completions')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='topic_completions') # NEW FK
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, related_name='topic_completions') # Changed to FK
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='topic_completions') # Changed to FK
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name='topic_completions') # Changed to FK
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='topic_completion_records') # Optional FK
    tema_number = models.CharField(max_length=10, blank=True, null=True)
    tema_title = models.TextField()
    completion_date = models.DateField()
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.teacher.full_name} - {self.grade_level.code} - P{self.periodo.number} - {self.paralelo.code} - Tema {self.tema_number}: {self.completion_date} ({self.academic_year.year})"

    class Meta:
        # Update unique_together (removing tema_title, using FKs)
        unique_together = ('teacher', 'academic_year', 'grade_level', 'periodo', 'paralelo', 'tema_number', 'subject') # Added subject? Maybe too strict again. Reconsider.
        # Let's try without subject first for uniqueness, similar to previous issue
        unique_together = ('teacher', 'academic_year', 'grade_level', 'periodo', 'paralelo', 'tema_number')
        ordering = ['teacher', 'academic_year', 'grade_level', 'periodo__number', 'completion_date']
        verbose_name_plural = "Topic Completion Records"