# academics/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class AcademicYear(models.Model):
    """Represents a school academic year."""
    year = models.PositiveSmallIntegerField(unique=True, verbose_name=_("Año")) # e.g., 2025
    start_date = models.DateField(verbose_name=_("Fecha de Inicio"))
    end_date = models.DateField(verbose_name=_("Fecha de Fin"))
    is_active = models.BooleanField(default=True, verbose_name=_("Activo")) # Maybe only one is active

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['-year']
        verbose_name = _("Año Académico")
        verbose_name_plural = _("Años Académicos")

class Trimestre(models.Model):
    """Represents a trimester within an academic year."""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='trimestres')
    number = models.PositiveSmallIntegerField(verbose_name=_("Número")) # 1, 2, or 3
    name = models.CharField(max_length=50, verbose_name=_("Nombre")) # e.g., "1er Trimestre"
    start_date = models.DateField(verbose_name=_("Fecha de Inicio"), null=True, blank=True)
    end_date = models.DateField(verbose_name=_("Fecha de Fin"), null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.academic_year.year})"

    class Meta:
        unique_together = ('academic_year', 'number')
        ordering = ['academic_year', 'number']
        verbose_name = _("Trimestre")
        verbose_name_plural = _("Trimestres")

class Periodo(models.Model):
    """Represents a Periodo within a Trimestre (2 periodos per trimestre)."""
    trimestre = models.ForeignKey(Trimestre, on_delete=models.CASCADE, related_name='periodos')
    number = models.PositiveSmallIntegerField(verbose_name=_("Número Total")) # 1 through 6
    name = models.CharField(max_length=50, verbose_name=_("Nombre")) # e.g., "1er Periodo"
    # Optional: Dates might be better derived from Trimestre/Year unless they vary significantly
    start_date = models.DateField(verbose_name=_("Fecha de Inicio"), null=True, blank=True)
    end_date = models.DateField(verbose_name=_("Fecha de Fin"), null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.trimestre.academic_year.year})"

    class Meta:
        # Assumes period numbers are unique within an academic year implicitly via trimestre link
        unique_together = ('trimestre', 'number') # Or maybe just ('academic_year', 'number') if easier? Let's try within Trimestre.
        ordering = ['trimestre__academic_year', 'number']
        verbose_name = _("Periodo")
        verbose_name_plural = _("Periodos")


class GradeLevel(models.Model):
    """Represents a specific grade level, categorized by educational stage."""
    # Define choices for the new stages using abbreviations for storage
    STAGE_CHOICES = [
        ('PRE', _('Preparatorio')),
        ('PRO', _('Profundización')),
        ('EXP', _('Expansión')),
    ]

    code = models.CharField(max_length=10, unique=True, primary_key=True, verbose_name=_("Código")) # e.g., '1S', '6P'
    name = models.CharField(max_length=100, verbose_name=_("Nombre Completo")) # e.g., "1ro de Secundaria"

    # Changed field name from 'level' to 'stage' for clarity, updated choices and length
    stage = models.CharField(
        max_length=3, # To store 'PRE', 'PRO', 'EXP'
        choices=STAGE_CHOICES,
        verbose_name=_("Etapa"),
        default='PRE', # Default to Preparatorio
    )
    # Added explicit order field for logical sorting
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Orden"),
        help_text=_("Orden para clasificación (e.g., 1=Pre, 2=Pro, 3=Exp)")
    )

    def __str__(self):
        # Display the full name like "1ro de Secundaria"
        return self.name

    class Meta:
        # Update ordering to use the new 'order' field primarily
        ordering = ['order', 'code']
        verbose_name = _("Grado")
        verbose_name_plural = _("Grados")


class Paralelo(models.Model):
    """Represents a parallel class group (A, B, C, D)."""
    code = models.CharField(max_length=1, unique=True, primary_key=True, verbose_name=_("Código")) # 'A', 'B', 'C', 'D'
    name = models.CharField(max_length=50, blank=True, verbose_name=_("Nombre Descriptivo")) # Optional, e.g., "Paralelo A"

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['code']
        verbose_name = _("Paralelo")
        verbose_name_plural = _("Paralelos")


class Subject(models.Model):
    """Represents a subject taught (e.g., Música, Matemáticas)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nombre Asignatura"))
    # Optional: Area (e.g., Ciencias Sociales, Artes) could be another FK or CharField

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Asignatura")
        verbose_name_plural = _("Asignaturas")

class TeacherAssignment(models.Model):
    """Defines which Subject a Teacher teaches for a specific Class (Grade+Paralelo) in an AcademicYear."""
    # --- CHANGE Teacher to a string reference ---
    teacher = models.ForeignKey(
        'teachers.Teacher', # Use 'app_label.ModelName' string
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_("Docente")
    )
    # --- /CHANGE ---
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='teacher_assignments', verbose_name=_("Año Académico"))
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, related_name='teacher_assignments', verbose_name=_("Grado"))
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name='teacher_assignments', verbose_name=_("Paralelo"))
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='teacher_assignments', verbose_name=_("Asignatura"))

    # ... (Meta and __str__ remain the same) ...
    class Meta:
        unique_together = ('teacher', 'academic_year', 'grade_level', 'paralelo')
        verbose_name = _("Asignación Docente por Clase")
        verbose_name_plural = _("Asignaciones Docentes por Clase")
        ordering = ['academic_year', 'teacher', 'grade_level', 'paralelo']

    def __str__(self):
         # __str__ might need adjustment later if teacher isn't loaded yet,
         # but for migrations this should be fine. A common pattern is:
         # try:
         #     teacher_name = self.teacher.full_name
         # except Teacher.DoesNotExist: # Need to import Teacher from teachers.models here *inside* the method
         #     teacher_name = "[Deleted Teacher]"
         # return f"{teacher_name} - {self.subject.name} ({self.grade_level.code}{self.paralelo.code}) - {self.academic_year.year}"
         # For now, keep it simple:
        return f"Assignment for Teacher ID {self.teacher_id} - {self.subject.name} ({self.grade_level.code}{self.paralelo.code}) - {self.academic_year.year}"

