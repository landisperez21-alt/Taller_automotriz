from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from taller.roles import asignar_rol_inicial

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Inicio de sesión con la casilla «Mantener mi cuenta abierta»."""

    mantener_sesion = forms.BooleanField(
        required=False,
        label="Mantener mi cuenta abierta",
        widget=forms.CheckboxInput(attrs={"class": "check"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "username",
             "placeholder": "tu_usuario", "autofocus": True}
        )
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "current-password",
             "placeholder": "••••••••"}
        )


class RegistroForm(UserCreationForm):
    """
    Registro público. La cuenta creada NUNCA es staff ni superusuario: recibe
    únicamente el rol de solo lectura «Consulta».
    """

    first_name = forms.CharField(label="Nombres", max_length=60)
    last_name = forms.CharField(label="Apellidos", max_length=60)
    email = forms.EmailField(label="Correo electrónico")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        autocompletar = {"username": "username", "first_name": "given-name",
                         "last_name": "family-name", "email": "email",
                         "password1": "new-password", "password2": "new-password"}
        for nombre, campo in self.fields.items():
            campo.widget.attrs["class"] = "form-control"
            campo.widget.attrs["autocomplete"] = autocompletar.get(nombre, "off")

    def clean_email(self):
        correo = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=correo).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return correo

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.is_active = True
        if commit:
            usuario.save()
            asignar_rol_inicial(usuario)
        return usuario
