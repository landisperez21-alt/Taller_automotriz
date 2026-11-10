from decimal import Decimal

from django.db import models, transaction

from taller.models.repuesto import Repuesto
from taller.validators import validar_mayor_cero, validar_no_negativo


class OrdenServicio(models.Model):
    """Trabajo realizado a partir de un diagnóstico (un tipo de repuesto por orden)."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROCESO = "en_proceso", "En proceso"
        FINALIZADA = "finalizada", "Finalizada"

    diagnostico = models.ForeignKey(
        "taller.Diagnostico", on_delete=models.PROTECT, related_name="ordenes"
    )
    repuesto = models.ForeignKey(
        "taller.Repuesto", on_delete=models.PROTECT, related_name="ordenes"
    )
    descripcion_trabajo = models.TextField()
    cantidad_repuesto = models.PositiveIntegerField(
        default=1, validators=[validar_mayor_cero]
    )
    costo_mano_obra = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validar_no_negativo]
    )
    # Se calcula automáticamente: mano de obra + cantidad × precio del repuesto.
    costo_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False
    )
    fecha_inicio = models.DateField()
    fecha_entrega = models.DateField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )

    class Meta:
        ordering = ["-fecha_inicio", "-id"]
        verbose_name = "Orden de servicio"
        verbose_name_plural = "Órdenes de servicio"

    # ---- Atajos de lectura para reportes --------------------------------
    @property
    def numero(self):
        return f"OS-{self.pk:05d}" if self.pk else "OS-—"

    @property
    def cita(self):
        return self.diagnostico.cita

    @property
    def vehiculo(self):
        return self.diagnostico.cita.vehiculo

    @property
    def cliente(self):
        return self.diagnostico.cita.vehiculo.cliente

    @property
    def mecanico(self):
        return self.diagnostico.cita.mecanico

    @property
    def costo_repuestos(self):
        """Importe de repuestos tal como quedó registrado al guardar la orden."""
        return self.costo_total - self.costo_mano_obra

    @property
    def precio_unitario(self):
        if not self.cantidad_repuesto:
            return Decimal("0.00")
        return (self.costo_repuestos / self.cantidad_repuesto).quantize(Decimal("0.01"))

    # ---- Persistencia ---------------------------------------------------
    def calcular_total(self):
        return self.costo_mano_obra + self.cantidad_repuesto * self.repuesto.precio

    def save(self, *args, **kwargs):
        """Calcula el total y mantiene coherente el stock del repuesto."""
        self.costo_total = self.calcular_total()
        with transaction.atomic():
            if self.pk:
                previo = (
                    OrdenServicio.objects.filter(pk=self.pk)
                    .values("repuesto_id", "cantidad_repuesto")
                    .first()
                )
                if previo:
                    Repuesto.mover_stock(previo["repuesto_id"], previo["cantidad_repuesto"])
            Repuesto.mover_stock(self.repuesto_id, -self.cantidad_repuesto)
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Al eliminar la orden se devuelven las unidades al inventario."""
        with transaction.atomic():
            Repuesto.mover_stock(self.repuesto_id, self.cantidad_repuesto)
            return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} · {self.diagnostico.cita.vehiculo.placa}"
