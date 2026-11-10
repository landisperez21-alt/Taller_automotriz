"""
CRUD genérico para las siete tablas de negocio.

Cada vista valida el permiso de Django correspondiente (view/add/change/delete),
de modo que los roles definidos en `taller/roles.py` controlan qué puede hacer
cada usuario.
"""
from functools import reduce
from operator import and_, or_
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from taller.modulos import MODULOS, construir_celda

POR_PAGINA = 12


def _modulo(slug):
    try:
        return MODULOS[slug]
    except KeyError:
        raise Http404("El módulo solicitado no existe.")


def _exigir(request, modulo, accion):
    if not request.user.has_perm(modulo.permiso(accion)):
        raise PermissionDenied


def _permisos(request, modulo):
    u = request.user
    return {
        "crear": u.has_perm(modulo.permiso("add")),
        "editar": u.has_perm(modulo.permiso("change")),
        "eliminar": u.has_perm(modulo.permiso("delete")),
    }


def _filtrar(consulta, campos):
    """Todas las palabras deben aparecer en alguno de los campos (AND de ORs)."""
    terminos = [t for t in consulta.split() if t]
    if not terminos:
        return Q()
    por_termino = [
        reduce(or_, (Q(**{f"{campo}__icontains": t}) for campo in campos))
        for t in terminos
    ]
    return reduce(and_, por_termino)


@login_required
@require_http_methods(["GET", "HEAD"])
def crud_list(request, slug):
    modulo = _modulo(slug)
    _exigir(request, modulo, "view")

    consulta = request.GET.get("q", "").strip()[:100]
    estado = request.GET.get("estado", "").strip()

    objetos = modulo.modelo.objects.all()
    if modulo.relacionados:
        objetos = objetos.select_related(*modulo.relacionados)
    if consulta:
        objetos = objetos.filter(_filtrar(consulta, modulo.busqueda))
    if estado and estado in dict(modulo.opciones_estado):
        objetos = objetos.filter(estado=estado)
    else:
        estado = ""

    pagina = Paginator(objetos, POR_PAGINA).get_page(request.GET.get("page"))

    filas = [
        {
            "objeto": objeto,
            "celdas": [construir_celda(objeto, columna) for columna in modulo.columnas],
        }
        for objeto in pagina.object_list
    ]

    parametros = {k: v for k, v in (("q", consulta), ("estado", estado)) if v}
    return render(request, "taller/crud/list.html", {
        "modulo": modulo,
        "slug": slug,
        "pagina": pagina,
        "filas": filas,
        "consulta": consulta,
        "estado_activo": estado,
        "qs_filtros": urlencode(parametros),
        "permisos": _permisos(request, modulo),
        "puede_documento": modulo.documento,
    })


def _guardar(request, modulo, instancia=None):
    Formulario = modulo.formulario
    form = Formulario(request.POST or None, instance=instancia)
    if request.method == "POST" and form.is_valid():
        objeto = form.save()
        verbo = "actualizad" if instancia else "registrad"
        messages.success(
            request, f"{modulo.singular} {modulo.participio(verbo)} correctamente."
        )
        return objeto, form
    return None, form


@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def crud_create(request, slug):
    modulo = _modulo(slug)
    _exigir(request, modulo, "add")
    objeto, form = _guardar(request, modulo)
    if objeto:
        return redirect("crud_list", slug=slug)
    return render(request, "taller/crud/form.html", {
        "modulo": modulo, "slug": slug, "form": form,
        "titulo_accion": f"Nuevo {modulo.singular.lower()}" if not modulo.femenino
        else f"Nueva {modulo.singular.lower()}",
        "boton": "Registrar",
        "objeto": None,
    })


@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def crud_edit(request, slug, pk):
    modulo = _modulo(slug)
    _exigir(request, modulo, "change")
    instancia = get_object_or_404(modulo.modelo, pk=pk)
    objeto, form = _guardar(request, modulo, instancia)
    if objeto:
        return redirect("crud_list", slug=slug)
    return render(request, "taller/crud/form.html", {
        "modulo": modulo, "slug": slug, "form": form,
        "titulo_accion": f"Editar {modulo.singular.lower()}",
        "boton": "Guardar cambios",
        "objeto": instancia,
    })


@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def crud_delete(request, slug, pk):
    modulo = _modulo(slug)
    _exigir(request, modulo, "delete")
    objeto = get_object_or_404(modulo.modelo, pk=pk)

    if request.method == "POST":
        try:
            objeto.delete()
            messages.success(
                request, f"{modulo.singular} {modulo.participio('eliminad')} correctamente."
            )
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar: el registro está vinculado a otros datos "
                "(por ejemplo vehículos, citas, diagnósticos u órdenes).",
            )
        return redirect("crud_list", slug=slug)

    return render(request, "taller/crud/delete.html", {
        "modulo": modulo, "slug": slug, "objeto": objeto,
    })
