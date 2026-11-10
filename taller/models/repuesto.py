from django.db import models

from taller.validators import validar_codigo, validar_no_negativo


class Repuesto(models.Model):
    """Pieza de inventario. El estado se deriva automáticamente del stock."""

    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        AGOTADO = "agotado", "Agotado"

    codigo = models.CharField(max_length=30, unique=True, validators=[validar_codigo])
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    marca = models.CharField(max_length=100)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validar_no_negativo]
    )
    stock = models.PositiveIntegerField(default=0)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"

    def save(self, *args, **kwargs):
        self.estado = self.Estado.AGOTADO if self.stock <= 0 else self.Estado.DISPONIBLE
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "estado" not in update_fields:
            kwargs["update_fields"] = [*update_fields, "estado"]
        super().save(*args, **kwargs)

    @classmethod
    def mover_stock(cls, repuesto_id, delta):
        """Suma (o resta, si delta < 0) unidades al stock de forma segura.

        Debe llamarse dentro de una transacción (`transaction.atomic`).
        """
        repuesto = cls.objects.select_for_update().get(pk=repuesto_id)
        repuesto.stock = max(0, repuesto.stock + delta)
        repuesto.save(update_fields=["stock", "estado"])
        return repuesto

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"
