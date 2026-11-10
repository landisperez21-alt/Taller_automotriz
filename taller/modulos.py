"""
Registro declarativo de los siete módulos de negocio.

Cada módulo describe qué modelo/formulario usa, qué columnas muestra la lista,
en qué campos busca y qué icono tiene en el menú. Las vistas CRUD genéricas
(`taller/views/crud.py`), el menú lateral y los permisos se alimentan de aquí.
"""
from dataclasses import dataclass

from taller import formato
from taller.forms import (
    CitaForm,
    ClienteForm,
    DiagnosticoForm,
    MecanicoForm,
    OrdenServicioForm,
    RepuestoForm,
    VehiculoForm,
)
from taller.models import (
    Cita,
    Cliente,
    Diagnostico,
    Mecanico,
    OrdenServicio,
    Repuesto,
    Vehiculo,
)


@dataclass(frozen=True)
class Columna:
    titulo: str
    accesor: str = ""
    tipo: str = "texto"  # texto | codigo | fecha | hora | moneda | entero | estado | largo


@dataclass(frozen=True)
class Modulo:
    slug: str
    titulo: str
    singular: str
    femenino: bool
    icono: str
    descripcion: str
    modelo: type
    formulario: type
    columnas: tuple
    busqueda: tuple
    relacionados: tuple = ()
    tiene_estado: bool = False
    documento: bool = False  # ¿tiene documento imprimible individual?

    @property
    def nombre_modelo(self):
        return self.modelo._meta.model_name

    def permiso(self, accion):
        return f"taller.{accion}_{self.nombre_modelo}"

    @property
    def opciones_estado(self):
        return self.modelo._meta.get_field("estado").choices if self.tiene_estado else ()

    def participio(self, verbo):
        """«creado» / «creada», según el género del módulo."""
        return f"{verbo}{'a' if self.femenino else 'o'}"


MODULOS = {
    m.slug: m
    for m in (
        Modulo(
            slug="clientes", titulo="Clientes", singular="Cliente", femenino=False,
            icono="users", modelo=Cliente, formulario=ClienteForm,
            descripcion="Propietarios de los vehículos que atiende el taller.",
            columnas=(
                Columna("Cliente", "nombre_completo"),
                Columna("DNI", "dni", "codigo"),
                Columna("Teléfono", "telefono"),
                Columna("Correo", "correo"),
                Columna("Registrado", "created_at", "fecha"),
            ),
            busqueda=("nombres", "apellidos", "dni", "telefono", "correo"),
        ),
        Modulo(
            slug="vehiculos", titulo="Vehículos", singular="Vehículo", femenino=False,
            icono="car", modelo=Vehiculo, formulario=VehiculoForm,
            descripcion="Flota registrada con su propietario y kilometraje.",
            columnas=(
                Columna("Placa", "placa", "codigo"),
                Columna("Vehículo", "descripcion"),
                Columna("Color", "color"),
                Columna("Km", "kilometraje", "entero"),
                Columna("Propietario", "cliente.nombre_completo"),
            ),
            busqueda=("placa", "marca", "modelo", "color", "cliente__nombres",
                      "cliente__apellidos", "cliente__dni"),
            relacionados=("cliente",),
        ),
        Modulo(
            slug="mecanicos", titulo="Mecánicos", singular="Mecánico", femenino=False,
            icono="wrench", modelo=Mecanico, formulario=MecanicoForm,
            descripcion="Personal técnico y su especialidad.",
            columnas=(
                Columna("Mecánico", "nombre_completo"),
                Columna("DNI", "dni", "codigo"),
                Columna("Especialidad", "especialidad"),
                Columna("Teléfono", "telefono"),
                Columna("Estado", "estado", "estado"),
            ),
            busqueda=("nombres", "apellidos", "dni", "especialidad", "correo"),
            tiene_estado=True,
        ),
        Modulo(
            slug="citas", titulo="Citas", singular="Cita", femenino=True,
            icono="calendar", modelo=Cita, formulario=CitaForm,
            descripcion="Agenda de visitas de vehículos al taller.",
            columnas=(
                Columna("Fecha", "fecha", "fecha"),
                Columna("Hora", "hora", "hora"),
                Columna("Vehículo", "vehiculo.placa", "codigo"),
                Columna("Cliente", "vehiculo.cliente.nombre_completo"),
                Columna("Mecánico", "mecanico.nombre_completo"),
                Columna("Motivo", "motivo", "largo"),
                Columna("Estado", "estado", "estado"),
            ),
            busqueda=("vehiculo__placa", "vehiculo__cliente__nombres",
                      "vehiculo__cliente__apellidos", "mecanico__nombres",
                      "mecanico__apellidos", "motivo"),
            relacionados=("vehiculo__cliente", "mecanico"),
            tiene_estado=True, documento=True,
        ),
        Modulo(
            slug="diagnosticos", titulo="Diagnósticos", singular="Diagnóstico", femenino=False,
            icono="activity", modelo=Diagnostico, formulario=DiagnosticoForm,
            descripcion="Evaluaciones técnicas con causa, solución y costo estimado.",
            columnas=(
                Columna("Fecha", "fecha", "fecha"),
                Columna("Vehículo", "cita.vehiculo.placa", "codigo"),
                Columna("Cliente", "cita.vehiculo.cliente.nombre_completo"),
                Columna("Mecánico", "cita.mecanico.nombre_completo"),
                Columna("Problema", "descripcion_problema", "largo"),
                Columna("Costo estimado", "costo_estimado", "moneda"),
            ),
            busqueda=("cita__vehiculo__placa", "cita__vehiculo__cliente__nombres",
                      "cita__vehiculo__cliente__apellidos", "cita__mecanico__apellidos",
                      "descripcion_problema", "causa"),
            relacionados=("cita__vehiculo__cliente", "cita__mecanico"),
            documento=True,
        ),
        Modulo(
            slug="repuestos", titulo="Repuestos", singular="Repuesto", femenino=False,
            icono="package", modelo=Repuesto, formulario=RepuestoForm,
            descripcion="Inventario de piezas, precios y stock disponible.",
            columnas=(
                Columna("Código", "codigo", "codigo"),
                Columna("Repuesto", "nombre"),
                Columna("Marca", "marca"),
                Columna("Precio", "precio", "moneda"),
                Columna("Stock", "stock", "entero"),
                Columna("Estado", "estado", "estado"),
            ),
            busqueda=("codigo", "nombre", "marca", "descripcion"),
            tiene_estado=True,
        ),
        Modulo(
            slug="ordenes", titulo="Órdenes de servicio", singular="Orden de servicio",
            femenino=True, icono="clipboard", modelo=OrdenServicio, formulario=OrdenServicioForm,
            descripcion="Trabajos, repuestos utilizados y costos finales.",
            columnas=(
                Columna("N.º", "numero", "codigo"),
                Columna("Vehículo", "diagnostico.cita.vehiculo.placa", "codigo"),
                Columna("Cliente", "diagnostico.cita.vehiculo.cliente.nombre_completo"),
                Columna("Mecánico", "diagnostico.cita.mecanico.nombre_completo"),
                Columna("Entrega", "fecha_entrega", "fecha"),
                Columna("Total", "costo_total", "moneda"),
                Columna("Estado", "estado", "estado"),
            ),
            busqueda=("diagnostico__cita__vehiculo__placa",
                      "diagnostico__cita__vehiculo__cliente__nombres",
                      "diagnostico__cita__vehiculo__cliente__apellidos",
                      "diagnostico__cita__mecanico__apellidos", "repuesto__nombre",
                      "descripcion_trabajo"),
            relacionados=("diagnostico__cita__vehiculo__cliente", "diagnostico__cita__mecanico",
                          "repuesto"),
            tiene_estado=True, documento=True,
        ),
    )
}


# ---------------------------------------------------------------------------
# Construcción de celdas para las listas
# ---------------------------------------------------------------------------
def resolver(objeto, ruta):
    """Recorre «a.b.c» sobre el objeto (llamando a lo invocable)."""
    actual = objeto
    for parte in ruta.split("."):
        if actual is None:
            return None
        actual = getattr(actual, parte)
        if callable(actual):
            actual = actual()
    return actual


def construir_celda(objeto, columna):
    if columna.tipo == "estado":
        valor = getattr(objeto, columna.accesor)
        return {
            "titulo": columna.titulo,
            "tipo": "estado",
            "texto": getattr(objeto, f"get_{columna.accesor}_display")(),
            "clase": formato.CLASES_ESTADO.get(valor, "muted"),
        }

    valor = resolver(objeto, columna.accesor)
    if columna.tipo == "fecha":
        texto = formato.formatear_fecha(valor)
    elif columna.tipo == "hora":
        texto = formato.formatear_hora(valor)
    elif columna.tipo == "moneda":
        texto = formato.formatear_moneda(valor)
    elif columna.tipo == "entero":
        texto = formato.formatear_entero(valor)
    else:
        texto = "—" if valor in (None, "") else str(valor)
        if columna.tipo == "largo" and len(texto) > 70:
            texto = texto[:67].rstrip() + "…"
    return {"titulo": columna.titulo, "tipo": columna.tipo, "texto": texto, "clase": ""}
