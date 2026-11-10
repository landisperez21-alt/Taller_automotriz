"""Funciones de formato compartidas por vistas, plantillas y reportes."""
from datetime import date, datetime, time
from decimal import Decimal

from django.utils import timezone


def formatear_moneda(valor):
    if valor in (None, ""):
        return "—"
    return f"S/ {Decimal(valor):,.2f}"


def formatear_fecha(valor):
    if valor in (None, ""):
        return "—"
    if isinstance(valor, datetime):
        if timezone.is_aware(valor):
            valor = timezone.localtime(valor)
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def formatear_hora(valor):
    if valor in (None, ""):
        return "—"
    if isinstance(valor, (time, datetime)):
        return valor.strftime("%H:%M")
    return str(valor)


def formatear_entero(valor):
    if valor in (None, ""):
        return "—"
    return f"{int(valor):,}"


# Clase de color (badge) según el valor almacenado del estado.
CLASES_ESTADO = {
    "pendiente": "warn",
    "confirmada": "info",
    "atendida": "ok",
    "cancelada": "danger",
    "en_proceso": "info",
    "finalizada": "ok",
    "activo": "ok",
    "inactivo": "muted",
    "disponible": "ok",
    "agotado": "danger",
}
