"""Formularios (ModelForm) de las siete tablas de negocio con sus validaciones."""
from datetime import time
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.utils import timezone

from taller.models import (
    Cita,
    Cliente,
    Diagnostico,
    Mecanico,
    OrdenServicio,
    Repuesto,
    Vehiculo,
)

from .base import TallerBaseForm

HORA_APERTURA = time(7, 0)
HORA_CIERRE = time(20, 0)
LIMITE_IMPORTE = Decimal("99999999.99")


# ---------------------------------------------------------------------------
# 01 Cliente
# ---------------------------------------------------------------------------
class ClienteForm(TallerBaseForm):
    class Meta:
        model = Cliente
        fields = ["nombres", "apellidos", "dni", "telefono", "correo", "direccion"]
        labels = {"dni": "DNI", "telefono": "Teléfono", "correo": "Correo electrónico",
                  "direccion": "Dirección"}
        widgets = {
            "dni": forms.TextInput(attrs={"inputmode": "numeric", "maxlength": 8,
                                          "pattern": r"\d{8}", "data-digits": "",
                                          "placeholder": "8 dígitos"}),
            "telefono": forms.TextInput(attrs={"type": "tel", "placeholder": "+51 987 654 321"}),
            "correo": forms.EmailInput(attrs={"placeholder": "cliente@correo.com"}),
        }

    def clean_nombres(self):
        return self.limpiar_espacios(self.cleaned_data["nombres"])

    def clean_apellidos(self):
        return self.limpiar_espacios(self.cleaned_data["apellidos"])

    def clean_correo(self):
        return self.cleaned_data["correo"].strip().lower()


# ---------------------------------------------------------------------------
# 02 Vehículo
# ---------------------------------------------------------------------------
class VehiculoForm(TallerBaseForm):
    class Meta:
        model = Vehiculo
        fields = ["cliente", "placa", "marca", "modelo", "anio", "color", "kilometraje"]
        labels = {"anio": "Año", "kilometraje": "Kilometraje (km)"}
        widgets = {
            "placa": forms.TextInput(attrs={"data-uppercase": "", "maxlength": 10,
                                            "placeholder": "ABC-123"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.order_by("apellidos", "nombres")
        self.fields["cliente"].label_from_instance = (
            lambda c: f"{c.nombre_completo} · DNI {c.dni}"
        )

    def clean_placa(self):
        return self.cleaned_data["placa"].replace(" ", "").upper()

    def clean_marca(self):
        return self.limpiar_espacios(self.cleaned_data["marca"])

    def clean_modelo(self):
        return self.limpiar_espacios(self.cleaned_data["modelo"])

    def clean_color(self):
        return self.limpiar_espacios(self.cleaned_data["color"])


# ---------------------------------------------------------------------------
# 03 Mecánico
# ---------------------------------------------------------------------------
class MecanicoForm(TallerBaseForm):
    class Meta:
        model = Mecanico
        fields = ["nombres", "apellidos", "dni", "especialidad", "telefono", "correo", "estado"]
        labels = {"dni": "DNI", "telefono": "Teléfono", "correo": "Correo electrónico"}
        widgets = {
            "dni": forms.TextInput(attrs={"inputmode": "numeric", "maxlength": 8,
                                          "pattern": r"\d{8}", "data-digits": "",
                                          "placeholder": "8 dígitos"}),
            "telefono": forms.TextInput(attrs={"type": "tel"}),
            "especialidad": forms.TextInput(attrs={"placeholder": "Frenos, motor, electricidad…"}),
        }

    def clean_nombres(self):
        return self.limpiar_espacios(self.cleaned_data["nombres"])

    def clean_apellidos(self):
        return self.limpiar_espacios(self.cleaned_data["apellidos"])

    def clean_especialidad(self):
        return self.limpiar_espacios(self.cleaned_data["especialidad"])

    def clean_correo(self):
        return self.cleaned_data["correo"].strip().lower()


# ---------------------------------------------------------------------------
# 04 Cita
# ---------------------------------------------------------------------------
class CitaForm(TallerBaseForm):
    class Meta:
        model = Cita
        fields = ["vehiculo", "mecanico", "fecha", "hora", "motivo", "estado", "observaciones"]
        labels = {"vehiculo": "Vehículo", "mecanico": "Mecánico"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vehiculo = self.fields["vehiculo"]
        vehiculo.queryset = Vehiculo.objects.select_related("cliente").order_by("placa")
        vehiculo.label_from_instance = (
            lambda v: f"{v.placa} · {v.marca} {v.modelo} — {v.cliente.nombre_completo}"
        )

        # Solo mecánicos activos (más el ya asignado si se edita una cita antigua).
        filtro = Q(estado=Mecanico.Estado.ACTIVO)
        if self.instance.pk and self.instance.mecanico_id:
            filtro |= Q(pk=self.instance.mecanico_id)
        self.fields["mecanico"].queryset = Mecanico.objects.filter(filtro).order_by(
            "apellidos", "nombres"
        )
        self.fields["mecanico"].label_from_instance = (
            lambda m: f"{m.nombre_completo} · {m.especialidad}"
        )

        if not self.instance.pk:
            self.fields["fecha"].initial = timezone.localdate()

    def clean_motivo(self):
        return self.limpiar_espacios(self.cleaned_data["motivo"])

    def clean(self):
        datos = super().clean()
        fecha, hora = datos.get("fecha"), datos.get("hora")
        mecanico, estado = datos.get("mecanico"), datos.get("estado")

        if mecanico and mecanico.estado != Mecanico.Estado.ACTIVO and (
            not self.instance.pk or self.instance.mecanico_id != mecanico.pk
        ):
            self.add_error("mecanico", "El mecánico seleccionado está inactivo.")

        if hora and not (HORA_APERTURA <= hora <= HORA_CIERRE):
            self.add_error(
                "hora",
                f"El taller atiende de {HORA_APERTURA:%H:%M} a {HORA_CIERRE:%H:%M}.",
            )

        activa = estado in (Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA)
        if fecha and activa and (not self.instance.pk or "fecha" in self.changed_data):
            if fecha < timezone.localdate():
                self.add_error("fecha", "No se puede programar una cita en una fecha pasada.")

        if fecha and hora and mecanico and estado != Cita.Estado.CANCELADA:
            choque = (
                Cita.objects.filter(mecanico=mecanico, fecha=fecha, hora=hora)
                .exclude(estado=Cita.Estado.CANCELADA)
                .exclude(pk=self.instance.pk)
            )
            if choque.exists():
                self.add_error(
                    "hora", "Ese mecánico ya tiene una cita en esa fecha y hora."
                )
        return datos


# ---------------------------------------------------------------------------
# 05 Diagnóstico
# ---------------------------------------------------------------------------
class DiagnosticoForm(TallerBaseForm):
    class Meta:
        model = Diagnostico
        fields = ["cita", "fecha", "descripcion_problema", "causa",
                  "solucion_recomendada", "costo_estimado"]
        labels = {
            "descripcion_problema": "Descripción del problema",
            "solucion_recomendada": "Solución recomendada",
            "costo_estimado": "Costo estimado (S/)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filtro = ~Q(estado=Cita.Estado.CANCELADA)
        if self.instance.pk:
            filtro |= Q(pk=self.instance.cita_id)
        cita = self.fields["cita"]
        cita.queryset = (
            Cita.objects.filter(filtro)
            .select_related("vehiculo__cliente", "mecanico")
            .order_by("-fecha", "-hora")
        )
        cita.label_from_instance = lambda c: (
            f"#{c.pk} · {c.fecha:%d/%m/%Y} {c.hora:%H:%M} · {c.vehiculo.placa} · "
            f"{c.vehiculo.cliente.nombre_completo}"
        )
        if not self.instance.pk:
            self.fields["fecha"].initial = timezone.localdate()

    def clean(self):
        datos = super().clean()
        fecha, cita = datos.get("fecha"), datos.get("cita")
        if fecha and fecha > timezone.localdate():
            self.add_error("fecha", "La fecha del diagnóstico no puede ser futura.")
        if fecha and cita and fecha < cita.fecha:
            self.add_error(
                "fecha",
                f"No puede ser anterior a la fecha de la cita ({cita.fecha:%d/%m/%Y}).",
            )
        return datos


# ---------------------------------------------------------------------------
# 06 Repuesto
# ---------------------------------------------------------------------------
class RepuestoForm(TallerBaseForm):
    """El estado (Disponible/Agotado) se calcula solo a partir del stock."""

    class Meta:
        model = Repuesto
        fields = ["codigo", "nombre", "marca", "precio", "stock", "descripcion"]
        labels = {"codigo": "Código", "precio": "Precio unitario (S/)",
                  "descripcion": "Descripción"}
        widgets = {"codigo": forms.TextInput(attrs={"data-uppercase": "", "maxlength": 30,
                                                    "placeholder": "FIL-ACE-001"})}

    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()

    def clean_nombre(self):
        return self.limpiar_espacios(self.cleaned_data["nombre"])

    def clean_marca(self):
        return self.limpiar_espacios(self.cleaned_data["marca"])


# ---------------------------------------------------------------------------
# 07 Orden de servicio
# ---------------------------------------------------------------------------
class RepuestoSelect(forms.Select):
    """Select que expone precio y stock en cada opción (para el total en vivo)."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opcion = super().create_option(name, value, label, selected, index, subindex, attrs)
        instancia = getattr(value, "instance", None)
        if instancia is not None:
            opcion["attrs"]["data-precio"] = str(instancia.precio)
            opcion["attrs"]["data-stock"] = str(instancia.stock)
        return opcion


class OrdenServicioForm(TallerBaseForm):
    class Meta:
        model = OrdenServicio
        fields = ["diagnostico", "repuesto", "cantidad_repuesto", "descripcion_trabajo",
                  "costo_mano_obra", "fecha_inicio", "fecha_entrega", "estado"]
        labels = {
            "diagnostico": "Diagnóstico",
            "cantidad_repuesto": "Cantidad de repuesto",
            "descripcion_trabajo": "Trabajos realizados",
            "costo_mano_obra": "Mano de obra (S/)",
            "fecha_inicio": "Inicio del servicio",
            "fecha_entrega": "Entrega programada",
        }
        widgets = {"repuesto": RepuestoSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Valores guardados antes de editar: sirven para validar el stock real.
        self._previo = (
            (self.instance.repuesto_id, self.instance.cantidad_repuesto)
            if self.instance.pk
            else None
        )

        diagnostico = self.fields["diagnostico"]
        diagnostico.queryset = Diagnostico.objects.select_related(
            "cita__vehiculo__cliente", "cita__mecanico"
        ).order_by("-fecha", "-id")
        diagnostico.label_from_instance = lambda d: (
            f"#{d.pk} · {d.fecha:%d/%m/%Y} · {d.cita.vehiculo.placa} · "
            f"{d.cita.vehiculo.cliente.nombre_completo}"
        )

        filtro = Q(estado=Repuesto.Estado.DISPONIBLE)
        if self._previo:
            filtro |= Q(pk=self._previo[0])
        repuesto = self.fields["repuesto"]
        repuesto.queryset = Repuesto.objects.filter(filtro).order_by("nombre")
        repuesto.label_from_instance = (
            lambda r: f"{r.codigo} · {r.nombre} (stock {r.stock})"
        )

        if not self.instance.pk:
            hoy = timezone.localdate()
            self.fields["fecha_inicio"].initial = hoy
            self.fields["fecha_entrega"].initial = hoy

    def clean_descripcion_trabajo(self):
        return self.cleaned_data["descripcion_trabajo"].strip()

    def clean(self):
        datos = super().clean()
        repuesto = datos.get("repuesto")
        cantidad = datos.get("cantidad_repuesto")
        mano_obra = datos.get("costo_mano_obra")
        inicio, entrega = datos.get("fecha_inicio"), datos.get("fecha_entrega")
        diagnostico = datos.get("diagnostico")

        if inicio and entrega and entrega < inicio:
            self.add_error("fecha_entrega", "La entrega no puede ser anterior al inicio.")
        if inicio and diagnostico and inicio < diagnostico.fecha:
            self.add_error(
                "fecha_inicio",
                f"No puede ser anterior al diagnóstico ({diagnostico.fecha:%d/%m/%Y}).",
            )

        if repuesto and cantidad:
            disponibles = repuesto.stock
            if self._previo and self._previo[0] == repuesto.pk:
                disponibles += self._previo[1]  # unidades que esta misma orden ya reservó
            if cantidad > disponibles:
                self.add_error(
                    "cantidad_repuesto",
                    f"Stock insuficiente: solo hay {disponibles} unidad(es) de "
                    f"«{repuesto.nombre}».",
                )
            elif mano_obra is not None:
                if mano_obra + cantidad * repuesto.precio > LIMITE_IMPORTE:
                    self.add_error("cantidad_repuesto", "El importe total excede el máximo permitido.")
        return datos
