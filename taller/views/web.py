"""Vistas web: autenticación, dashboard, reportes y documentos imprimibles."""
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from taller import formato
from taller.forms import LoginForm, RegistroForm
from taller.forms.reportes import FiltroReporteForm
from taller.models import Cita, Cliente, Diagnostico, OrdenServicio, Repuesto, Vehiculo
from taller.modulos import MODULOS

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
LIMITE_FILAS_REPORTE = 500


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------
def _clave_intentos(request, usuario):
    ip = request.META.get("REMOTE_ADDR", "desconocida")
    return f"login-fallos:{ip}:{usuario.strip().lower()[:150]}"


def _destino_seguro(request):
    destino = request.POST.get("next") or request.GET.get("next") or ""
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return destino
    return settings.LOGIN_REDIRECT_URL


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method != "POST":
        return render(request, "registration/login.html", {
            "form": LoginForm(request), "next": request.GET.get("next", ""),
        })

    usuario = request.POST.get("username", "")
    clave = _clave_intentos(request, usuario)

    if cache.get(clave, 0) >= settings.LOGIN_MAX_INTENTOS:
        minutos = max(1, settings.LOGIN_BLOQUEO_SEGUNDOS // 60)
        messages.error(
            request,
            f"Demasiados intentos fallidos. Espera {minutos} minuto(s) e inténtalo de nuevo.",
        )
        return render(request, "registration/login.html", {
            "form": LoginForm(request), "next": request.POST.get("next", ""),
        }, status=429)

    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        cache.delete(clave)
        login(request, form.get_user())
        # «Mantener mi cuenta abierta»: sesión persistente; si no, expira al cerrar el navegador.
        if form.cleaned_data.get("mantener_sesion"):
            request.session.set_expiry(settings.SESSION_REMEMBER_SECONDS)
        else:
            request.session.set_expiry(0)
        return redirect(_destino_seguro(request))

    cache.set(clave, cache.get(clave, 0) + 1, settings.LOGIN_BLOQUEO_SEGUNDOS)
    return render(request, "registration/login.html", {
        "form": form, "next": request.POST.get("next", ""),
    })


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()  # sin is_staff / is_superuser; solo rol «Consulta»
        messages.success(
            request,
            "Cuenta creada. Inicia sesión; tu acceso inicial es de solo consulta "
            "hasta que un administrador te asigne más permisos.",
        )
        return redirect("login")
    return render(request, "registration/register.html", {"form": form})


@login_required
@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("login")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def calcular_kpis():
    """Indicadores calculados en vivo con el ORM."""
    hoy = timezone.localdate()
    ingresos = (
        OrdenServicio.objects.filter(estado=OrdenServicio.Estado.FINALIZADA)
        .aggregate(total=Sum("costo_total"))["total"]
        or Decimal("0")
    )
    activas = [Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA]
    return {
        "clientes": Cliente.objects.count(),
        "vehiculos": Vehiculo.objects.count(),
        "citas": Cita.objects.count(),
        "citas_hoy": Cita.objects.filter(fecha=hoy, estado__in=activas).count(),
        "citas_pendientes": Cita.objects.filter(estado__in=activas).count(),
        "diagnosticos": Diagnostico.objects.count(),
        "diagnosticos_mes": Diagnostico.objects.filter(
            fecha__year=hoy.year, fecha__month=hoy.month
        ).count(),
        "ordenes": OrdenServicio.objects.count(),
        "ordenes_proceso": OrdenServicio.objects.filter(
            estado=OrdenServicio.Estado.EN_PROCESO
        ).count(),
        "ordenes_finalizadas": OrdenServicio.objects.filter(
            estado=OrdenServicio.Estado.FINALIZADA
        ).count(),
        "ingresos": formato.formatear_moneda(ingresos),
        "repuestos_agotados": Repuesto.objects.filter(
            estado=Repuesto.Estado.AGOTADO
        ).count(),
        "actualizado": timezone.localtime().strftime("%H:%M:%S"),
    }


def _distribucion(modelo):
    """Conteo por estado con porcentaje para las barras del dashboard."""
    conteo = dict(
        modelo.objects.values_list("estado").annotate(n=Count("id")).order_by()
    )
    total = sum(conteo.values()) or 1
    return [
        {
            "etiqueta": etiqueta,
            "n": conteo.get(valor, 0),
            "pct": round(conteo.get(valor, 0) * 100 / total),
            "clase": formato.CLASES_ESTADO.get(valor, "muted"),
        }
        for valor, etiqueta in modelo._meta.get_field("estado").choices
    ]


def _ingresos_semestre():
    """Ingresos (órdenes finalizadas) de los últimos 6 meses."""
    hoy = timezone.localdate()
    meses = []
    anio, mes = hoy.year, hoy.month
    for _ in range(6):
        meses.append((anio, mes))
        mes -= 1
        if mes == 0:
            anio, mes = anio - 1, 12
    meses.reverse()

    inicio = date(meses[0][0], meses[0][1], 1)
    filas = (
        OrdenServicio.objects.filter(
            estado=OrdenServicio.Estado.FINALIZADA, fecha_inicio__gte=inicio
        )
        .values("fecha_inicio__year", "fecha_inicio__month")
        .annotate(total=Sum("costo_total"))
        .order_by()
    )
    totales = {(f["fecha_inicio__year"], f["fecha_inicio__month"]): f["total"] or 0 for f in filas}
    maximo = max([float(v) for v in totales.values()] + [1.0])
    return [
        {
            "etiqueta": MESES[m - 1],
            "valor": formato.formatear_moneda(totales.get((a, m), 0)),
            "alto": max(4, round(float(totales.get((a, m), 0)) * 100 / maximo)),
        }
        for a, m in meses
    ]


@login_required
def dashboard(request):
    u = request.user
    contexto = {
        "kpis": calcular_kpis(),
        "dist_citas": _distribucion(Cita),
        "dist_ordenes": _distribucion(OrdenServicio),
        "ingresos_meses": _ingresos_semestre(),
        "citas_proximas": [],
        "ordenes_recientes": [],
        "repuestos_alerta": [],
    }
    if u.has_perm("taller.view_cita"):
        contexto["citas_proximas"] = (
            Cita.objects.filter(
                fecha__gte=timezone.localdate(),
                estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
            )
            .select_related("vehiculo__cliente", "mecanico")
            .order_by("fecha", "hora")[:6]
        )
    if u.has_perm("taller.view_ordenservicio"):
        contexto["ordenes_recientes"] = (
            OrdenServicio.objects.select_related(
                "diagnostico__cita__vehiculo__cliente", "repuesto"
            ).order_by("-id")[:6]
        )
    if u.has_perm("taller.view_repuesto"):
        contexto["repuestos_alerta"] = Repuesto.objects.filter(
            Q(estado=Repuesto.Estado.AGOTADO) | Q(stock__lte=3)
        ).order_by("stock", "nombre")[:6]
    return render(request, "taller/dashboard.html", contexto)


@login_required
@never_cache
def api_kpis(request):
    """Endpoint JSON que el dashboard consulta cada 30 s."""
    return JsonResponse(calcular_kpis())


# ---------------------------------------------------------------------------
# Reportes filtrables
# ---------------------------------------------------------------------------
REPORTES = {
    "citas": {
        "titulo": "Reporte de citas",
        "modulo": "citas",
        "plantilla": "taller/reportes/_tabla_citas.html",
    },
    "diagnosticos": {
        "titulo": "Reporte de diagnósticos",
        "modulo": "diagnosticos",
        "plantilla": "taller/reportes/_tabla_diagnosticos.html",
    },
    "ordenes": {
        "titulo": "Reporte de órdenes de servicio",
        "modulo": "ordenes",
        "plantilla": "taller/reportes/_tabla_ordenes.html",
    },
}

_BUSQUEDA_REPORTE = {
    "citas": ("vehiculo__placa", "vehiculo__cliente__nombres", "vehiculo__cliente__apellidos",
              "vehiculo__cliente__dni", "motivo"),
    "diagnosticos": ("cita__vehiculo__placa", "cita__vehiculo__cliente__nombres",
                     "cita__vehiculo__cliente__apellidos", "cita__vehiculo__cliente__dni",
                     "descripcion_problema", "causa"),
    "ordenes": ("diagnostico__cita__vehiculo__placa",
                "diagnostico__cita__vehiculo__cliente__nombres",
                "diagnostico__cita__vehiculo__cliente__apellidos",
                "diagnostico__cita__vehiculo__cliente__dni", "repuesto__nombre",
                "descripcion_trabajo"),
}
_RUTA_MECANICO = {
    "citas": "mecanico",
    "diagnosticos": "cita__mecanico",
    "ordenes": "diagnostico__cita__mecanico",
}
_CAMPO_FECHA = {"citas": "fecha", "diagnosticos": "fecha", "ordenes": "fecha_inicio"}


def _exigir_reporte(request, tipo):
    if tipo not in REPORTES:
        raise Http404("Reporte no disponible.")
    modulo = MODULOS[REPORTES[tipo]["modulo"]]
    if not request.user.has_perm(modulo.permiso("view")):
        raise PermissionDenied
    return modulo


def _consulta_base(tipo):
    if tipo == "citas":
        return Cita.objects.select_related("vehiculo__cliente", "mecanico").prefetch_related(
            "diagnosticos"
        )
    if tipo == "diagnosticos":
        return Diagnostico.objects.select_related("cita__vehiculo__cliente", "cita__mecanico")
    return OrdenServicio.objects.select_related(
        "diagnostico__cita__vehiculo__cliente", "diagnostico__cita__mecanico", "repuesto"
    )


def _aplicar_filtros(tipo, consulta, filtros):
    campo_fecha = _CAMPO_FECHA[tipo]
    if filtros.get("desde"):
        consulta = consulta.filter(**{f"{campo_fecha}__gte": filtros["desde"]})
    if filtros.get("hasta"):
        consulta = consulta.filter(**{f"{campo_fecha}__lte": filtros["hasta"]})
    if filtros.get("estado"):
        consulta = consulta.filter(estado=filtros["estado"])
    if filtros.get("mecanico"):
        consulta = consulta.filter(**{_RUTA_MECANICO[tipo]: filtros["mecanico"]})
    for termino in (filtros.get("q") or "").split():
        condicion = Q()
        for campo in _BUSQUEDA_REPORTE[tipo]:
            condicion |= Q(**{f"{campo}__icontains": termino})
        consulta = consulta.filter(condicion)
    return consulta


def _totales(tipo, consulta):
    if tipo == "citas":
        agregado = consulta.aggregate(
            total=Count("id", distinct=True), costo=Sum("diagnosticos__costo_estimado")
        )
        return {"cantidad": agregado["total"], "costo_estimado": agregado["costo"] or Decimal("0")}
    if tipo == "diagnosticos":
        agregado = consulta.aggregate(total=Count("id"), costo=Sum("costo_estimado"))
        return {"cantidad": agregado["total"], "costo_estimado": agregado["costo"] or Decimal("0")}
    agregado = consulta.aggregate(
        total=Count("id"), mano_obra=Sum("costo_mano_obra"), importe=Sum("costo_total")
    )
    mano_obra = agregado["mano_obra"] or Decimal("0")
    importe = agregado["importe"] or Decimal("0")
    return {
        "cantidad": agregado["total"],
        "mano_obra": mano_obra,
        "repuestos": importe - mano_obra,
        "total": importe,
    }


@login_required
def reportes_index(request):
    disponibles = [
        {"tipo": tipo, "titulo": datos["titulo"], "modulo": MODULOS[datos["modulo"]]}
        for tipo, datos in REPORTES.items()
        if request.user.has_perm(MODULOS[datos["modulo"]].permiso("view"))
    ]
    if not disponibles:
        raise PermissionDenied
    return render(request, "taller/reportes/index.html", {"reportes": disponibles})


@login_required
def reporte(request, tipo):
    modulo = _exigir_reporte(request, tipo)
    form = FiltroReporteForm(tipo, request.GET or None)
    filtros = form.cleaned_data if form.is_bound and form.is_valid() else {}

    consulta = _aplicar_filtros(tipo, _consulta_base(tipo), filtros)
    totales = _totales(tipo, consulta)
    filas = list(consulta[:LIMITE_FILAS_REPORTE])

    resumen = []
    if filtros.get("desde") or filtros.get("hasta"):
        resumen.append(
            f"Periodo: {formato.formatear_fecha(filtros.get('desde'))} – "
            f"{formato.formatear_fecha(filtros.get('hasta'))}"
        )
    if filtros.get("estado"):
        resumen.append(f"Estado: {dict(form.fields['estado'].choices).get(filtros['estado'])}")
    if filtros.get("mecanico"):
        resumen.append(f"Mecánico: {filtros['mecanico']}")
    if filtros.get("q"):
        resumen.append(f"Búsqueda: «{filtros['q']}»")

    return render(request, "taller/reportes/reporte.html", {
        "tipo": tipo,
        "modulo": modulo,
        "titulo": REPORTES[tipo]["titulo"],
        "plantilla_tabla": REPORTES[tipo]["plantilla"],
        "form": form,
        "filas": filas,
        "totales": totales,
        "resumen": resumen,
        "truncado": totales["cantidad"] > LIMITE_FILAS_REPORTE,
        "limite": LIMITE_FILAS_REPORTE,
        "generado": timezone.localtime(),
    })


@login_required
def documento(request, tipo, pk):
    """Documento imprimible de un registro (cita, diagnóstico u orden)."""
    modulo = _exigir_reporte(request, tipo)
    objeto = get_object_or_404(_consulta_base(tipo), pk=pk)

    contexto = {
        "tipo": tipo,
        "modulo": modulo,
        "objeto": objeto,
        "generado": timezone.localtime(),
    }
    if tipo == "citas":
        contexto["diagnosticos"] = list(objeto.diagnosticos.all())
        contexto["total_diagnosticos"] = sum(
            (d.costo_estimado for d in contexto["diagnosticos"]), Decimal("0")
        )
        contexto["ordenes"] = list(
            OrdenServicio.objects.filter(diagnostico__cita=objeto).select_related("repuesto")
        )
    elif tipo == "diagnosticos":
        contexto["ordenes"] = list(objeto.ordenes.select_related("repuesto"))
    if "ordenes" in contexto:
        contexto["total_ordenes"] = sum(
            (o.costo_total for o in contexto["ordenes"]), Decimal("0")
        )
    return render(request, "taller/reportes/documento.html", contexto)
