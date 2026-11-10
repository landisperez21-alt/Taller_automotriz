from django import forms


class TallerBaseForm(forms.ModelForm):
    """
    Formulario base de los modelos del taller.

    Centraliza estilos, tipos HTML5 (date/time/number) y utilidades de limpieza
    para que cada formulario concreto solo declare sus reglas de negocio.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            widget = campo.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "check"
                continue

            clases = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{clases} form-control".strip()

            if isinstance(campo, forms.DateField):
                widget.input_type = "date"
                widget.format = "%Y-%m-%d"
                campo.input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
            elif isinstance(campo, forms.TimeField):
                widget.input_type = "time"
                widget.format = "%H:%M"
                campo.input_formats = ["%H:%M", "%H:%M:%S"]
            elif isinstance(campo, forms.DecimalField):
                widget.attrs.setdefault("step", "0.01")
                widget.attrs.setdefault("min", "0")
                widget.attrs.setdefault("inputmode", "decimal")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)

    def full_clean(self):
        super().full_clean()
        # Accesibilidad: marca como inválidos los campos con error.
        if self.is_bound:
            for nombre in self.errors:
                campo = self.fields.get(nombre)
                if campo is not None:
                    campo.widget.attrs["aria-invalid"] = "true"

    @staticmethod
    def limpiar_espacios(valor):
        """Quita espacios sobrantes (inicio, fin y repetidos)."""
        return " ".join((valor or "").split())
