from django.contrib import admin

from taller.models import (
    Cita,
    Cliente,
    Diagnostico,
    Mecanico,
    OrdenServicio,
    Repuesto,
    Vehiculo,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("apellidos", "nombres", "dni", "telefono", "correo", "created_at")
    search_fields = ("nombres", "apellidos", "dni", "correo")


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "anio", "cliente", "kilometraje")
    search_fields = ("placa", "marca", "modelo", "cliente__apellidos")
    list_select_related = ("cliente",)


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ("apellidos", "nombres", "especialidad", "telefono", "estado")
    list_filter = ("estado",)
    search_fields = ("nombres", "apellidos", "dni", "especialidad")


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "vehiculo", "mecanico", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("vehiculo__placa", "motivo")
    list_select_related = ("vehiculo", "mecanico")


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "cita", "costo_estimado")
    list_filter = ("fecha",)
    search_fields = ("descripcion_problema", "causa", "cita__vehiculo__placa")


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "marca", "precio", "stock", "estado")
    list_filter = ("estado",)
    search_fields = ("codigo", "nombre", "marca")


@admin.register(OrdenServicio)
class OrdenServicioAdmin(admin.ModelAdmin):
    list_display = ("id", "diagnostico", "repuesto", "fecha_inicio", "fecha_entrega",
                    "costo_total", "estado")
    list_filter = ("estado", "fecha_inicio")
    readonly_fields = ("costo_total",)
