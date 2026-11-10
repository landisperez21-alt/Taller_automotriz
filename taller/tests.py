"""
Pruebas automáticas: python manage.py test

Cubren autenticación (sin privilegios automáticos), permisos por rol, CRUD,
cálculo de la orden de servicio, inventario y reportes.
"""
from datetime import date, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from taller.forms import CitaForm
from taller.models import Cita, Cliente, Diagnostico, Mecanico, OrdenServicio, Repuesto, Vehiculo
from taller.roles import ROL_ADMIN_TALLER, ROL_CONSULTA

User = get_user_model()
CLAVE = "Clave#Segura2026"


def crear_datos():
    cliente = Cliente.objects.create(
        nombres="Carlos", apellidos="Quispe", dni="45871236", telefono="987654321",
        correo="carlos@correo.com", direccion="Av. Lima 123",
    )
    vehiculo = Vehiculo.objects.create(
        cliente=cliente, placa="ABC-123", marca="Toyota", modelo="Corolla",
        anio=2018, color="Blanco", kilometraje=50000,
    )
    mecanico = Mecanico.objects.create(
        nombres="Ricardo", apellidos="Paredes", dni="41236587", especialidad="Motor",
        telefono="951234780", correo="ricardo@motortech.pe",
    )
    hoy = timezone.localdate()
    cita = Cita.objects.create(
        vehiculo=vehiculo, mecanico=mecanico, fecha=hoy, hora=time(10, 0),
        motivo="Mantenimiento", estado=Cita.Estado.CONFIRMADA,
    )
    diagnostico = Diagnostico.objects.create(
        cita=cita, fecha=hoy, descripcion_problema="Ruido", causa="Desgaste",
        solucion_recomendada="Cambiar pieza", costo_estimado=Decimal("150.00"),
    )
    repuesto = Repuesto.objects.create(
        codigo="FIL-001", nombre="Filtro de aceite", marca="Bosch",
        precio=Decimal("30.00"), stock=10,
    )
    return cliente, vehiculo, mecanico, cita, diagnostico, repuesto


class ModelosTests(TestCase):
    def test_siete_modelos_de_negocio(self):
        nombres = {m.__name__ for m in (Cliente, Vehiculo, Mecanico, Cita, Diagnostico,
                                        Repuesto, OrdenServicio)}
        self.assertEqual(len(nombres), 7)

    def test_orden_calcula_total_y_descuenta_stock(self):
        *_, diagnostico, repuesto = crear_datos()
        orden = OrdenServicio.objects.create(
            diagnostico=diagnostico, repuesto=repuesto, cantidad_repuesto=3,
            descripcion_trabajo="Cambio de filtro", costo_mano_obra=Decimal("50.00"),
            fecha_inicio=date.today(), fecha_entrega=date.today(),
        )
        repuesto.refresh_from_db()
        self.assertEqual(orden.costo_total, Decimal("140.00"))  # 50 + 3 × 30
        self.assertEqual(repuesto.stock, 7)

        orden.delete()
        repuesto.refresh_from_db()
        self.assertEqual(repuesto.stock, 10)

    def test_repuesto_se_marca_agotado(self):
        *_, repuesto = crear_datos()
        repuesto.stock = 0
        repuesto.save()
        self.assertEqual(repuesto.estado, Repuesto.Estado.AGOTADO)


class AutenticacionTests(TestCase):
    def test_registro_no_otorga_privilegios(self):
        respuesta = self.client.post(reverse("registro"), {
            "username": "nuevo", "first_name": "Nuevo", "last_name": "Usuario",
            "email": "nuevo@correo.com", "password1": CLAVE, "password2": CLAVE,
        })
        self.assertRedirects(respuesta, reverse("login"))
        usuario = User.objects.get(username="nuevo")
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertEqual(list(usuario.groups.values_list("name", flat=True)), [ROL_CONSULTA])

    def test_login_mantener_cuenta_abierta(self):
        User.objects.create_user("persistente", password=CLAVE)
        self.client.post(reverse("login"), {
            "username": "persistente", "password": CLAVE, "mantener_sesion": "on",
        })
        self.assertEqual(self.client.session.get_expiry_age(), settings.SESSION_REMEMBER_SECONDS)

    def test_login_sin_mantener_expira_al_cerrar_navegador(self):
        User.objects.create_user("temporal", password=CLAVE)
        self.client.post(reverse("login"), {"username": "temporal", "password": CLAVE})
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_rechaza_credenciales_invalidas(self):
        User.objects.create_user("correcto", password=CLAVE)
        respuesta = self.client.post(reverse("login"), {"username": "correcto", "password": "mala"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_vistas_requieren_sesion(self):
        for nombre in ("dashboard", "reportes"):
            respuesta = self.client.get(reverse(nombre))
            self.assertEqual(respuesta.status_code, 302)
            self.assertIn(reverse("login"), respuesta["Location"])
        self.assertEqual(self.client.get(reverse("crud_list", args=["clientes"])).status_code, 302)


class PermisosTests(TestCase):
    def test_rol_consulta_solo_lectura(self):
        usuario = User.objects.create_user("lector", password=CLAVE)
        usuario.groups.add(Group.objects.get(name=ROL_CONSULTA))
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse("crud_list", args=["clientes"])).status_code, 200)
        self.assertEqual(self.client.get(reverse("crud_create", args=["clientes"])).status_code, 403)

    def test_administrador_del_taller_puede_crear(self):
        usuario = User.objects.create_user("jefe", password=CLAVE)
        usuario.groups.add(Group.objects.get(name=ROL_ADMIN_TALLER))
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse("crud_create", args=["clientes"])).status_code, 200)


class CrudTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_superuser("root", "root@correo.com", CLAVE)
        self.client.force_login(self.usuario)
        self.cliente, self.vehiculo, self.mecanico, self.cita, self.diagnostico, self.repuesto = crear_datos()

    def test_listas_de_los_siete_modulos(self):
        for slug in ("clientes", "vehiculos", "mecanicos", "citas", "diagnosticos",
                     "repuestos", "ordenes"):
            with self.subTest(slug=slug):
                self.assertEqual(self.client.get(reverse("crud_list", args=[slug])).status_code, 200)
                self.assertEqual(self.client.get(reverse("crud_create", args=[slug])).status_code, 200)

    def test_busqueda(self):
        respuesta = self.client.get(reverse("crud_list", args=["clientes"]), {"q": "quispe"})
        self.assertContains(respuesta, "Carlos Quispe")
        respuesta = self.client.get(reverse("crud_list", args=["clientes"]), {"q": "zzzz"})
        self.assertNotContains(respuesta, "Carlos Quispe")

    def test_crear_editar_y_eliminar_cliente(self):
        datos = {"nombres": "Ana", "apellidos": "Torres", "dni": "42365897", "telefono": "912457863",
                 "correo": "ana@correo.com", "direccion": "Jr. Cusco 10"}
        self.assertRedirects(self.client.post(reverse("crud_create", args=["clientes"]), datos),
                             reverse("crud_list", args=["clientes"]))
        ana = Cliente.objects.get(dni="42365897")

        datos["telefono"] = "999888777"
        self.client.post(reverse("crud_edit", args=["clientes", ana.pk]), datos)
        ana.refresh_from_db()
        self.assertEqual(ana.telefono, "999888777")

        self.client.post(reverse("crud_delete", args=["clientes", ana.pk]))
        self.assertFalse(Cliente.objects.filter(pk=ana.pk).exists())

    def test_validaciones_cliente(self):
        datos = {"nombres": "Ana", "apellidos": "Torres", "dni": "123", "telefono": "912457863",
                 "correo": "no-es-correo", "direccion": "Jr. Cusco 10"}
        respuesta = self.client.post(reverse("crud_create", args=["clientes"]), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.context["form"].is_valid())
        self.assertIn("dni", respuesta.context["form"].errors)
        self.assertIn("correo", respuesta.context["form"].errors)

    def test_dni_duplicado_rechazado(self):
        datos = {"nombres": "Otro", "apellidos": "Cliente", "dni": self.cliente.dni,
                 "telefono": "912457863", "correo": "otro@correo.com", "direccion": "Calle 1"}
        respuesta = self.client.post(reverse("crud_create", args=["clientes"]), datos)
        self.assertIn("dni", respuesta.context["form"].errors)

    def test_no_se_elimina_cliente_con_vehiculos(self):
        self.client.post(reverse("crud_delete", args=["clientes", self.cliente.pk]))
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_cita_no_permite_choque_de_horario(self):
        formulario = CitaForm(data={
            "vehiculo": self.vehiculo.pk, "mecanico": self.mecanico.pk,
            "fecha": (timezone.localdate()).isoformat(), "hora": "10:00",
            "motivo": "Otra revisión", "estado": Cita.Estado.PENDIENTE, "observaciones": "",
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn("hora", formulario.errors)

    def test_orden_via_formulario_valida_stock(self):
        url = reverse("crud_create", args=["ordenes"])
        base = {"diagnostico": self.diagnostico.pk, "repuesto": self.repuesto.pk,
                "descripcion_trabajo": "Cambio", "costo_mano_obra": "40.00",
                "fecha_inicio": date.today().isoformat(),
                "fecha_entrega": (date.today() + timedelta(days=1)).isoformat(),
                "estado": "pendiente"}
        # Más unidades que el stock → error
        respuesta = self.client.post(url, {**base, "cantidad_repuesto": "99"})
        self.assertIn("cantidad_repuesto", respuesta.context["form"].errors)
        # Cantidad válida → se crea y descuenta stock
        self.client.post(url, {**base, "cantidad_repuesto": "2"})
        self.repuesto.refresh_from_db()
        self.assertEqual(self.repuesto.stock, 8)
        self.assertEqual(OrdenServicio.objects.get().costo_total, Decimal("100.00"))


class ReportesYDashboardTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_superuser("root", "root@correo.com", CLAVE))
        *_, self.diagnostico, self.repuesto = crear_datos()
        self.orden = OrdenServicio.objects.create(
            diagnostico=self.diagnostico, repuesto=self.repuesto, cantidad_repuesto=2,
            descripcion_trabajo="Cambio de filtro", costo_mano_obra=Decimal("40.00"),
            fecha_inicio=date.today(), fecha_entrega=date.today(),
            estado=OrdenServicio.Estado.FINALIZADA,
        )

    def test_dashboard_y_api_de_kpis(self):
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
        datos = self.client.get(reverse("api_kpis")).json()
        for clave in ("clientes", "vehiculos", "citas", "diagnosticos", "ordenes"):
            self.assertEqual(datos[clave], 1)

    def test_reportes_filtrables(self):
        self.assertEqual(self.client.get(reverse("reportes")).status_code, 200)
        for tipo in ("citas", "diagnosticos", "ordenes"):
            with self.subTest(tipo=tipo):
                respuesta = self.client.get(reverse("reporte", args=[tipo]), {"q": "ABC"})
                self.assertContains(respuesta, "ABC-123")
                respuesta = self.client.get(reverse("reporte", args=[tipo]), {"q": "no-existe"})
                self.assertNotContains(respuesta, "ABC-123")

    def test_reporte_de_ordenes_desglosa_costos(self):
        respuesta = self.client.get(reverse("reporte", args=["ordenes"]))
        self.assertContains(respuesta, "S/ 100.00")  # 40 mano de obra + 2 × 30

    def test_documentos_imprimibles(self):
        for tipo, pk in (("citas", self.diagnostico.cita_id), ("diagnosticos", self.diagnostico.pk),
                         ("ordenes", self.orden.pk)):
            with self.subTest(tipo=tipo):
                respuesta = self.client.get(reverse("documento", args=[tipo, pk]))
                self.assertContains(respuesta, "Carlos Quispe")
                self.assertContains(respuesta, "ABC-123")
