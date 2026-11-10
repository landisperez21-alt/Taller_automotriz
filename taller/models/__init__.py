"""Siete modelos de negocio, cada uno en su propio archivo."""
from .cliente import Cliente
from .vehiculo import Vehiculo
from .mecanico import Mecanico
from .cita import Cita
from .diagnostico import Diagnostico
from .repuesto import Repuesto
from .orden_servicio import OrdenServicio

__all__ = [
    "Cliente",
    "Vehiculo",
    "Mecanico",
    "Cita",
    "Diagnostico",
    "Repuesto",
    "OrdenServicio",
]
