"""
Carga datos de ejemplo para probar el sistema.

    python manage.py cargar_demo             # clientes, vehículos, citas, etc.
    python manage.py cargar_demo --usuarios  # además crea 3 cuentas de prueba (solo DEBUG=True)

Si ya existen clientes no se vuelve a cargar nada (evita duplicados).
"""
from datetime import time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from taller.models import Cita, Cliente, Diagnostico, Mecanico, OrdenServicio, Repuesto, Vehiculo
from taller.roles import (
    ROL_ADMIN_TALLER,
    ROL_RECEPCION,
    ROL_TALLER,
    asegurar_grupos,
)

# usuario, contraseña, rol (ninguna cuenta es staff ni superusuario)
USUARIOS_DEMO = (
    ("jefe_demo", "Jefe#2026-Taller", ROL_ADMIN_TALLER),
    ("recepcion_demo", "Recep#2026-Taller", ROL_RECEPCION),
    ("taller_demo", "Taller#2026-Taller", ROL_TALLER),
)

CLIENTES = [
    ("Carlos", "Quispe Huamán", "45871236", "987654321", "carlos.quispe@correo.com", "Av. Arequipa 1450, Lima"),
    ("María", "Fernández Rojas", "40125879", "956321478", "maria.fernandez@correo.com", "Jr. Cusco 320, Miraflores"),
    ("Luis", "Ramírez Soto", "47896521", "944785632", "luis.ramirez@correo.com", "Calle Los Pinos 215, San Borja"),
    ("Ana", "Torres Vega", "42365897", "912457863", "ana.torres@correo.com", "Av. Universitaria 980, Los Olivos"),
    ("Jorge", "Mendoza Díaz", "46587412", "978456123", "jorge.mendoza@correo.com", "Psje. Las Flores 45, Surco"),
    ("Rosa", "Salazar Pinto", "44785963", "965478123", "rosa.salazar@correo.com", "Av. Brasil 2210, Jesús María"),
]

VEHICULOS = [  # índice de cliente, placa, marca, modelo, año, color, km
    (0, "ABC-123", "Toyota", "Corolla", 2018, "Blanco", 68500),
    (0, "BDF-482", "Hyundai", "Tucson", 2021, "Gris", 32100),
    (1, "CGH-731", "Kia", "Rio", 2019, "Rojo", 54200),
    (2, "DKL-905", "Nissan", "Sentra", 2017, "Negro", 91800),
    (3, "EMN-264", "Chevrolet", "Spark", 2020, "Azul", 41500),
    (4, "FPR-518", "Suzuki", "Swift", 2022, "Plata", 18700),
    (5, "GST-340", "Mazda", "CX-5", 2016, "Gris", 112300),
    (5, "HUV-077", "Volkswagen", "Gol", 2015, "Blanco", 134900),
]

MECANICOS = [
    ("Ricardo", "Paredes Luna", "41236587", "Motor y transmisión", "951234780", "ricardo.paredes@motortech.pe", "activo"),
    ("Daniel", "Cárdenas Ruiz", "43698521", "Frenos y suspensión", "952345871", "daniel.cardenas@motortech.pe", "activo"),
    ("Elena", "Vargas Núñez", "45201478", "Electricidad automotriz", "953456982", "elena.vargas@motortech.pe", "activo"),
    ("Hugo", "Linares Cruz", "40852136", "Aire acondicionado", "954567093", "hugo.linares@motortech.pe", "inactivo"),
]

REPUESTOS = [  # código, nombre, marca, precio, stock, descripción
    ("FIL-ACE-001", "Filtro de aceite", "Bosch", "28.50", 40, "Filtro de aceite para motores 1.4–2.0 L."),
    ("FIL-AIR-002", "Filtro de aire", "Mann", "45.00", 25, "Filtro de aire de panel."),
    ("PAS-FRE-010", "Pastillas de freno delanteras", "Brembo", "165.00", 12, "Juego de 4 pastillas cerámicas."),
    ("BUJ-IRI-020", "Bujía de iridio", "NGK", "38.90", 30, "Bujía de larga duración."),
    ("ACE-5W30-05", "Aceite sintético 5W-30 (galón)", "Mobil", "139.00", 18, "Aceite sintético para motor."),
    ("BAT-12V-045", "Batería 12V 45Ah", "Etna", "389.00", 6, "Batería libre de mantenimiento."),
    ("AMO-DEL-030", "Amortiguador delantero", "Monroe", "275.00", 4, "Amortiguador hidráulico, unidad."),
    ("CORR-DIS-040", "Correa de distribución", "Gates", "210.00", 3, "Kit de correa con tensor."),
]


class Command(BaseCommand):
    help = "Carga clientes, vehículos, mecánicos, citas, diagnósticos, repuestos y órdenes de ejemplo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--usuarios", action="store_true",
            help="Crea cuentas de prueba por rol (solo con DEBUG=True).",
        )

    def handle(self, *args, **opciones):
        asegurar_grupos()

        if opciones["usuarios"]:
            self._crear_usuarios()

        if Cliente.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Ya existen datos; no se cargó nada para evitar duplicados."))
            return

        with transaction.atomic():
            self._cargar()
        self.stdout.write(self.style.SUCCESS(
            "Datos de ejemplo cargados: 6 clientes, 8 vehículos, 4 mecánicos, "
            "8 repuestos, citas, diagnósticos y órdenes."))

    # ------------------------------------------------------------------
    def _crear_usuarios(self):
        if not settings.DEBUG:
            raise CommandError("Las cuentas de prueba solo se crean con DJANGO_DEBUG=True.")
        from django.contrib.auth.models import Group

        User = get_user_model()
        for usuario, clave, rol in USUARIOS_DEMO:
            obj, creado = User.objects.get_or_create(username=usuario)
            if creado:
                obj.set_password(clave)
                obj.is_staff = False
                obj.is_superuser = False
                obj.save()
            obj.groups.add(Group.objects.get(name=rol))
            estado = "creado" if creado else "ya existía"
            self.stdout.write(f"  · {usuario} ({rol}) — {estado}" + (f" · clave: {clave}" if creado else ""))

    def _cargar(self):
        hoy = timezone.localdate()

        clientes = [
            Cliente.objects.create(nombres=n, apellidos=a, dni=d, telefono=t, correo=c, direccion=dr)
            for n, a, d, t, c, dr in CLIENTES
        ]
        vehiculos = [
            Vehiculo.objects.create(cliente=clientes[i], placa=p, marca=m, modelo=mo,
                                    anio=an, color=co, kilometraje=km)
            for i, p, m, mo, an, co, km in VEHICULOS
        ]
        mecanicos = [
            Mecanico.objects.create(nombres=n, apellidos=a, dni=d, especialidad=e,
                                    telefono=t, correo=c, estado=es)
            for n, a, d, e, t, c, es in MECANICOS
        ]
        repuestos = [
            Repuesto.objects.create(codigo=c, nombre=n, marca=m, precio=Decimal(p), stock=s, descripcion=d)
            for c, n, m, p, s, d in REPUESTOS
        ]

        def cita(veh, mec, dias, hora, motivo, estado, obs=""):
            return Cita.objects.create(
                vehiculo=vehiculos[veh], mecanico=mecanicos[mec], fecha=hoy + timedelta(days=dias),
                hora=hora, motivo=motivo, estado=estado, observaciones=obs,
            )

        def diag(c, dias, problema, causa, solucion, costo):
            return Diagnostico.objects.create(
                cita=c, fecha=hoy + timedelta(days=dias), descripcion_problema=problema,
                causa=causa, solucion_recomendada=solucion, costo_estimado=Decimal(costo),
            )

        def orden(d, rep, cant, trabajo, mano, ini, ent, estado):
            return OrdenServicio.objects.create(
                diagnostico=d, repuesto=repuestos[rep], cantidad_repuesto=cant,
                descripcion_trabajo=trabajo, costo_mano_obra=Decimal(mano),
                fecha_inicio=hoy + timedelta(days=ini), fecha_entrega=hoy + timedelta(days=ent),
                estado=estado,
            )

        A, C, P, X = (Cita.Estado.ATENDIDA, Cita.Estado.CONFIRMADA,
                      Cita.Estado.PENDIENTE, Cita.Estado.CANCELADA)

        # Citas atendidas (pasado) con diagnóstico y orden, repartidas en varios meses
        c1 = cita(0, 0, -140, time(9, 0), "Mantenimiento de 70 000 km", A)
        d1 = diag(c1, -140, "Vibración en el motor y cambio de aceite vencido.",
                  "Aceite degradado y filtro saturado.", "Cambio de aceite y filtro.", "210.00")
        orden(d1, 0, 1, "Cambio de aceite sintético y filtro de aceite.", "60.00", -139, -139, "finalizada")

        c2 = cita(2, 1, -105, time(10, 30), "Frenos con ruido al detenerse", A)
        d2 = diag(c2, -105, "Chirrido al frenar y pedal esponjoso.",
                  "Pastillas delanteras desgastadas al límite.", "Reemplazar pastillas y rectificar discos.", "340.00")
        orden(d2, 2, 1, "Cambio de pastillas delanteras y limpieza de calipers.", "120.00", -104, -103, "finalizada")

        c3 = cita(3, 2, -70, time(11, 0), "El auto no enciende por las mañanas", A)
        d3 = diag(c3, -70, "Arranque difícil en frío.",
                  "Batería sulfatada con carga insuficiente.", "Reemplazar la batería.", "450.00")
        orden(d3, 5, 1, "Reemplazo de batería y prueba del alternador.", "50.00", -69, -69, "finalizada")

        c4 = cita(6, 0, -40, time(8, 30), "Pérdida de potencia", A)
        d4 = diag(c4, -40, "Tirones al acelerar y consumo elevado.",
                  "Bujías desgastadas.", "Reemplazo del juego de bujías.", "220.00")
        orden(d4, 3, 4, "Cambio de 4 bujías de iridio y limpieza del cuerpo de aceleración.", "90.00", -39, -38, "finalizada")

        c5 = cita(1, 1, -12, time(15, 0), "Rebote excesivo en baches", A)
        d5 = diag(c5, -12, "Suspensión delantera golpea en baches.",
                  "Amortiguador delantero con fuga de aceite.", "Cambiar amortiguador.", "390.00")
        orden(d5, 6, 1, "Reemplazo de amortiguador delantero izquierdo y alineamiento.", "140.00", -10, -9, "finalizada")

        # Trabajos en curso
        c6 = cita(4, 2, -3, time(9, 30), "Luz de check engine encendida", A)
        d6 = diag(c6, -3, "Testigo del motor encendido de forma intermitente.",
                  "Sensor de oxígeno con lecturas fuera de rango.", "Revisión eléctrica y cambio de bujías.", "260.00")
        orden(d6, 3, 4, "Diagnóstico con escáner y cambio de bujías.", "110.00", -2, 2, "en_proceso")

        c7 = cita(7, 0, -1, time(10, 0), "Correa de distribución en mal estado", A)
        d7 = diag(c7, -1, "Ruido metálico en la parte frontal del motor.",
                  "Correa de distribución agrietada.", "Cambio preventivo del kit de distribución.", "420.00")
        orden(d7, 7, 1, "Cambio del kit de correa de distribución.", "180.00", 0, 3, "pendiente")

        # Agenda futura y una cancelada
        cita(5, 1, 0, time(16, 0), "Revisión pre-viaje", C, "Cliente solicita revisión completa de frenos y llantas.")
        cita(0, 2, 1, time(9, 0), "Revisión del sistema eléctrico", C)
        cita(2, 0, 2, time(11, 30), "Cambio de aceite y filtros", P)
        cita(3, 1, 4, time(14, 0), "Alineamiento y balanceo", P)
        cita(4, 0, -6, time(12, 0), "Chequeo general", X, "El cliente canceló por viaje.")
