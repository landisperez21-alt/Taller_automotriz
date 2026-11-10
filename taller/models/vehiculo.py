from django.db import models

from taller.validators import validar_anio, validar_placa


class Vehiculo(models.Model):
    """Vehículo que pertenece a un cliente."""

    cliente = models.ForeignKey(
        "taller.Cliente", on_delete=models.PROTECT, related_name="vehiculos"
    )
    placa = models.CharField(max_length=10, unique=True, validators=[validar_placa])
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveIntegerField(validators=[validar_anio])
    color = models.CharField(max_length=30)
    kilometraje = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["placa"]
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    @property
    def descripcion(self):
        return f"{self.marca} {self.modelo} {self.anio}"

    def __str__(self):
        return f"{self.placa} · {self.marca} {self.modelo}"
