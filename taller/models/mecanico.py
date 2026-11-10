from django.db import models

from taller.validators import validar_dni, validar_nombre, validar_telefono


class Mecanico(models.Model):
    """Técnico del taller que atiende citas."""

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    nombres = models.CharField(max_length=100, validators=[validar_nombre])
    apellidos = models.CharField(max_length=100, validators=[validar_nombre])
    dni = models.CharField(max_length=8, unique=True, validators=[validar_dni])
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, validators=[validar_telefono])
    correo = models.EmailField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Mecánico"
        verbose_name_plural = "Mecánicos"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __str__(self):
        return self.nombre_completo
