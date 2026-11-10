from .auth import LoginForm, RegistroForm
from .base import TallerBaseForm
from .negocio import (
    CitaForm,
    ClienteForm,
    DiagnosticoForm,
    MecanicoForm,
    OrdenServicioForm,
    RepuestoForm,
    VehiculoForm,
)

__all__ = [
    "TallerBaseForm",
    "LoginForm",
    "RegistroForm",
    "ClienteForm",
    "VehiculoForm",
    "MecanicoForm",
    "CitaForm",
    "DiagnosticoForm",
    "RepuestoForm",
    "OrdenServicioForm",
]
