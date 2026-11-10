"""
Validadores reutilizables (funciones simples, fáciles de serializar en migraciones).
"""
import re
from datetime import date

from django.core.exceptions import ValidationError

_RE_NOMBRE = re.compile(r"[^\W\d_]+(?:[ '.\-]+[^\W\d_]+)*\.?")
_RE_DNI = re.compile(r"\d{8}")
_RE_TELEFONO = re.compile(r"\+?\d[\d\s\-]{5,18}\d")
_RE_PLACA = re.compile(r"[A-Z0-9][A-Z0-9\-]{4,9}", re.IGNORECASE)
_RE_CODIGO = re.compile(r"[A-Z0-9][A-Z0-9\-_./]{1,29}", re.IGNORECASE)

ANIO_MINIMO = 1950


def validar_nombre(valor):
    if not _RE_NOMBRE.fullmatch((valor or "").strip()):
        raise ValidationError(
            "Use solo letras, espacios, apóstrofes, puntos o guiones.",
            code="nombre_invalido",
        )


def validar_dni(valor):
    if not _RE_DNI.fullmatch(valor or ""):
        raise ValidationError(
            "El DNI debe tener exactamente 8 dígitos numéricos.", code="dni_invalido"
        )


def validar_telefono(valor):
    if not _RE_TELEFONO.fullmatch((valor or "").strip()):
        raise ValidationError(
            "Ingrese un teléfono válido (7 a 20 dígitos; puede incluir +, espacios o guiones).",
            code="telefono_invalido",
        )


def validar_placa(valor):
    if not _RE_PLACA.fullmatch(valor or ""):
        raise ValidationError(
            "La placa debe tener de 5 a 10 caracteres alfanuméricos (se permite guion).",
            code="placa_invalida",
        )


def validar_codigo(valor):
    if not _RE_CODIGO.fullmatch(valor or ""):
        raise ValidationError(
            "El código admite letras, números y los símbolos - _ . / (2 a 30 caracteres).",
            code="codigo_invalido",
        )


def validar_anio(valor):
    maximo = date.today().year + 1
    if valor is not None and not (ANIO_MINIMO <= valor <= maximo):
        raise ValidationError(
            f"El año debe estar entre {ANIO_MINIMO} y {maximo}.", code="anio_invalido"
        )


def validar_no_negativo(valor):
    if valor is not None and valor < 0:
        raise ValidationError("El valor no puede ser negativo.", code="negativo")


def validar_mayor_cero(valor):
    if valor is not None and valor <= 0:
        raise ValidationError("El valor debe ser mayor que cero.", code="no_positivo")
