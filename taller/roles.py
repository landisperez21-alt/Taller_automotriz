"""
Roles (grupos de Django) del taller.

Los usuarios que se registran por la web reciben solo el rol «Consulta»
(lectura). Ningún rol concede `is_staff` ni `is_superuser`: esos privilegios
solo se otorgan manualmente desde el panel de administración.
"""
from django.contrib.auth.models import Group, Permission

APP = "taller"
MODELOS = ("cliente", "vehiculo", "mecanico", "cita", "diagnostico", "repuesto", "ordenservicio")

ROL_CONSULTA = "Consulta"
ROL_RECEPCION = "Recepción"
ROL_TALLER = "Taller"
ROL_ADMIN_TALLER = "Administrador del taller"


def _codigos(acciones, modelos):
    return {f"{accion}_{modelo}" for accion in acciones for modelo in modelos}


# rol -> códigos de permiso de Django
ROLES = {
    # Solo lectura de todo el sistema.
    ROL_CONSULTA: _codigos(["view"], MODELOS),
    # Recepción: registra clientes, vehículos y agenda.
    ROL_RECEPCION: (
        _codigos(["view"], MODELOS)
        | _codigos(["add", "change"], ["cliente", "vehiculo", "cita"])
    ),
    # Personal técnico: diagnósticos, órdenes e inventario.
    ROL_TALLER: (
        _codigos(["view"], MODELOS)
        | _codigos(["add", "change"], ["diagnostico", "ordenservicio", "repuesto"])
        | _codigos(["change"], ["cita"])
    ),
    # Jefe de taller: gestión completa de las siete tablas (sin acceso al admin).
    ROL_ADMIN_TALLER: _codigos(["add", "change", "delete", "view"], MODELOS),
}


def asegurar_grupos():
    """Crea o actualiza los grupos y sus permisos (idempotente)."""
    permisos = {
        p.codename: p
        for p in Permission.objects.filter(content_type__app_label=APP)
    }
    for nombre, codigos in ROLES.items():
        grupo, _ = Group.objects.get_or_create(name=nombre)
        grupo.permissions.set([permisos[c] for c in codigos if c in permisos])


def asignar_rol_inicial(usuario):
    """Asigna el rol de solo lectura a una cuenta recién registrada."""
    grupo = Group.objects.filter(name=ROL_CONSULTA).first()
    if grupo is None or not grupo.permissions.exists():
        asegurar_grupos()
        grupo = Group.objects.get(name=ROL_CONSULTA)
    usuario.groups.add(grupo)
