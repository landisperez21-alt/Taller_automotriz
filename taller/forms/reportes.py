from django import forms

from taller.models import Cita, Mecanico, OrdenServicio


class FiltroReporteForm(forms.Form):
    """Filtros de los reportes (se envían por GET para poder compartir el enlace)."""

    desde = forms.DateField(required=False, label="Desde")
    hasta = forms.DateField(required=False, label="Hasta")
    estado = forms.ChoiceField(required=False, label="Estado")
    mecanico = forms.ModelChoiceField(
        required=False, label="Mecánico", queryset=Mecanico.objects.none(),
        empty_label="Todos los mecánicos",
    )
    q = forms.CharField(
        required=False, max_length=100, label="Buscar",
        widget=forms.TextInput(attrs={"placeholder": "Placa, cliente, DNI…"}),
    )

    def __init__(self, tipo, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["mecanico"].queryset = Mecanico.objects.order_by("apellidos", "nombres")

        if tipo == "citas":
            opciones = Cita.Estado.choices
        elif tipo == "ordenes":
            opciones = OrdenServicio.Estado.choices
        else:
            opciones = None

        if opciones is None:
            del self.fields["estado"]
        else:
            self.fields["estado"].choices = [("", "Todos los estados"), *opciones]

        for nombre, campo in self.fields.items():
            campo.widget.attrs["class"] = "form-control"
            if isinstance(campo, forms.DateField):
                campo.widget = forms.DateInput(
                    attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
                )
                campo.input_formats = ["%Y-%m-%d", "%d/%m/%Y"]

    def clean(self):
        datos = super().clean()
        desde, hasta = datos.get("desde"), datos.get("hasta")
        if desde and hasta and desde > hasta:
            self.add_error("hasta", "«Hasta» no puede ser anterior a «Desde».")
        return datos
