from django.urls import path, register_converter

from taller.converters import ModuloConverter, TipoDocumentoConverter
from taller.views import crud, web

register_converter(ModuloConverter, "modulo")
register_converter(TipoDocumentoConverter, "tipodoc")

urlpatterns = [
    # Autenticación
    path("login/", web.iniciar_sesion, name="login"),
    path("registro/", web.registro, name="registro"),
    path("logout/", web.cerrar_sesion, name="logout"),

    # Dashboard
    path("", web.dashboard, name="dashboard"),
    path("api/kpis/", web.api_kpis, name="api_kpis"),

    # Reportes y documentos imprimibles
    path("reportes/", web.reportes_index, name="reportes"),
    path("reportes/<tipodoc:tipo>/", web.reporte, name="reporte"),
    path("documento/<tipodoc:tipo>/<int:pk>/", web.documento, name="documento"),

    # CRUD de las siete tablas de negocio
    path("<modulo:slug>/", crud.crud_list, name="crud_list"),
    path("<modulo:slug>/nuevo/", crud.crud_create, name="crud_create"),
    path("<modulo:slug>/<int:pk>/editar/", crud.crud_edit, name="crud_edit"),
    path("<modulo:slug>/<int:pk>/eliminar/", crud.crud_delete, name="crud_delete"),
]
