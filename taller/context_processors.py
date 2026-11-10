"""Datos de navegación disponibles en todas las plantillas."""
from taller.modulos import MODULOS

SECCIONES_REPORTE = ("reportes", "reporte", "documento")


def navegacion(request):
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return {}

    coincidencia = getattr(request, "resolver_match", None)
    nombre = coincidencia.url_name if coincidencia else ""
    if nombre in SECCIONES_REPORTE:
        activa = "reportes"
    elif nombre == "dashboard":
        activa = "dashboard"
    else:
        activa = (coincidencia.kwargs.get("slug") if coincidencia else "") or ""

    menu = [
        {"slug": m.slug, "titulo": m.titulo, "icono": m.icono}
        for m in MODULOS.values()
        if usuario.has_perm(m.permiso("view"))
    ]
    puede_reportes = any(
        usuario.has_perm(MODULOS[s].permiso("view")) for s in ("citas", "diagnosticos", "ordenes")
    )
    return {"menu_modulos": menu, "puede_reportes": puede_reportes, "seccion_activa": activa}
