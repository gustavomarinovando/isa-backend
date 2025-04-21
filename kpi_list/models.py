from django.db import models
from django.utils.translation import gettext_lazy as _ # For potential translation later

class Month(models.Model):
    """Representa un mes calendario para propósitos de programación."""
    SPANISH_MONTH_CHOICES = [
        (1, _('Enero')), (2, _('Febrero')), (3, _('Marzo')), (4, _('Abril')),
        (5, _('Mayo')), (6, _('Junio')), (7, _('Julio')), (8, _('Agosto')),
        (9, _('Septiembre')), (10, _('Octubre')), (11, _('Noviembre')), (12, _('Diciembre')),
    ]
    number = models.PositiveSmallIntegerField(
        primary_key=True,
        choices=SPANISH_MONTH_CHOICES,
        verbose_name=_("Número de Mes"),
        help_text=_("Mes (1=Enero, 12=Diciembre)")
    )

    def __str__(self):
        # Get the display name from choices
        return self.get_number_display()

    class Meta:
        ordering = ['number']
        verbose_name = _("Mes")
        verbose_name_plural = _("Meses")
        # Consider adding a data migration to auto-populate months 1-12


class AcademicObjective(models.Model):
    """Representa un objetivo académico estratégico con el que se alinean los KPIs."""
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Nombre del Objetivo"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Descripción"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Objetivo Académico")
        verbose_name_plural = _("Objetivos Académicos")


class SGCObjective(models.Model):
    """Representa un objetivo del Sistema de Gestión de Calidad (SGC)."""
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Nombre del Objetivo SGC"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Descripción SGC"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Objetivo SGC")
        verbose_name_plural = _("Objetivos SGC")


class KPI(models.Model):
    """Representa un Indicador Clave de Desempeño (KPI) para la institución."""
    number = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("Número de KPI"),
        help_text=_("El número oficial (1-68) que identifica este KPI.")
    )
    name = models.CharField(
        max_length=500,
        verbose_name=_("Nombre Corto / Título"),
        help_text=_("El nombre corto o título del KPI.")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Descripción Detallada"),
        help_text=_("Descripción explicando el KPI, su propósito y método de cálculo.")
    )

    # --- Relationships ---
    academic_objective = models.ForeignKey(
        AcademicObjective,
        on_delete=models.SET_NULL, # Keep KPI if objective is deleted, just set this field null
        null=True, # Must be True if on_delete is SET_NULL
        blank=True, # Allow KPI to not have an academic objective in Admin/Forms
        related_name='kpis', # Allows objective.kpis.all() lookup
        verbose_name=_("Objetivo Académico Relacionado")
    )
    sgc_objective = models.ForeignKey(
        SGCObjective,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpis',
        verbose_name=_("Objetivo SGC Relacionado")
    )

    # --- Review Schedule ---
    review_months = models.ManyToManyField(
        Month,
        blank=True, # Allow KPI to have no specific review months selected
        verbose_name=_("Meses de Revisión"),
        help_text=_("Seleccione los meses en que este KPI debe ser revisado/reportado.")
    )

    # --- Potential Future Fields ---
    # data_source_type = models.CharField(...)
    # calculation_logic = models.TextField(...)
    # responsible_person = models.ForeignKey('auth.User', ...)

    def __str__(self):
        return f"KPI {self.number}: {self.name}"

    class Meta:
        ordering = ['number'] # Default sort order
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"