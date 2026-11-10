from django.db import models

from taller.validators import validar_no_negativo


class Diagnostico(models.Model):
    """Evaluación técnica realizada a partir de una cita."""

    cita = models.ForeignKey(
        "taller.Cita", on_delete=models.PROTECT, related_name="diagnosticos"
    )
    descripcion_problema = models.TextField()
    causa = models.TextField()
    solucion_recomendada = models.TextField()
    fecha = models.DateField()
    costo_estimado = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validar_no_negativo]
    )

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"

    # Atajos de lectura para reportes (todo se deriva de la cita).
    @property
    def vehiculo(self):
        return self.cita.vehiculo

    @property
    def cliente(self):
        return self.cita.vehiculo.cliente

    @property
    def mecanico(self):
        return self.cita.mecanico

    def __str__(self):
        return f"Diagnóstico #{self.pk} · {self.fecha:%d/%m/%Y} · {self.cita.vehiculo.placa}"
