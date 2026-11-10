from django.db import models


class Cita(models.Model):
    """Visita programada de un vehículo con un mecánico."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        ATENDIDA = "atendida", "Atendida"
        CANCELADA = "cancelada", "Cancelada"

    vehiculo = models.ForeignKey(
        "taller.Vehiculo", on_delete=models.PROTECT, related_name="citas"
    )
    mecanico = models.ForeignKey(
        "taller.Mecanico", on_delete=models.PROTECT, related_name="citas"
    )
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha", "-hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    @property
    def cliente(self):
        return self.vehiculo.cliente

    @property
    def costo_estimado_total(self):
        """Suma de los diagnósticos de la cita (usa prefetch si existe)."""
        return sum((d.costo_estimado for d in self.diagnosticos.all()), 0)

    def __str__(self):
        return f"Cita #{self.pk} · {self.fecha:%d/%m/%Y} {self.hora:%H:%M} · {self.vehiculo.placa}"
