from django.db import models

from taller.validators import validar_dni, validar_nombre, validar_telefono


class Cliente(models.Model):
    """Propietario de uno o varios vehículos."""

    nombres = models.CharField(max_length=100, validators=[validar_nombre])
    apellidos = models.CharField(max_length=100, validators=[validar_nombre])
    dni = models.CharField(max_length=8, unique=True, validators=[validar_dni])
    telefono = models.CharField(max_length=20, validators=[validar_telefono])
    correo = models.EmailField()
    direccion = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __str__(self):
        return self.nombre_completo
