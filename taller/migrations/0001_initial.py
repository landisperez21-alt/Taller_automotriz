import django.db.models.deletion
from django.db import migrations, models

import taller.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombres", models.CharField(max_length=100, validators=[taller.validators.validar_nombre])),
                ("apellidos", models.CharField(max_length=100, validators=[taller.validators.validar_nombre])),
                ("dni", models.CharField(max_length=8, unique=True, validators=[taller.validators.validar_dni])),
                ("telefono", models.CharField(max_length=20, validators=[taller.validators.validar_telefono])),
                ("correo", models.EmailField(max_length=254)),
                ("direccion", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Cliente",
                "verbose_name_plural": "Clientes",
                "ordering": ["apellidos", "nombres"],
            },
        ),
        migrations.CreateModel(
            name="Mecanico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombres", models.CharField(max_length=100, validators=[taller.validators.validar_nombre])),
                ("apellidos", models.CharField(max_length=100, validators=[taller.validators.validar_nombre])),
                ("dni", models.CharField(max_length=8, unique=True, validators=[taller.validators.validar_dni])),
                ("especialidad", models.CharField(max_length=100)),
                ("telefono", models.CharField(max_length=20, validators=[taller.validators.validar_telefono])),
                ("correo", models.EmailField(max_length=254)),
                (
                    "estado",
                    models.CharField(
                        choices=[("activo", "Activo"), ("inactivo", "Inactivo")],
                        default="activo",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "Mecánico",
                "verbose_name_plural": "Mecánicos",
                "ordering": ["apellidos", "nombres"],
            },
        ),
        migrations.CreateModel(
            name="Repuesto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=30, unique=True, validators=[taller.validators.validar_codigo])),
                ("nombre", models.CharField(max_length=150)),
                ("descripcion", models.TextField(blank=True)),
                ("marca", models.CharField(max_length=100)),
                (
                    "precio",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[taller.validators.validar_no_negativo],
                    ),
                ),
                ("stock", models.PositiveIntegerField(default=0)),
                (
                    "estado",
                    models.CharField(
                        choices=[("disponible", "Disponible"), ("agotado", "Agotado")],
                        default="disponible",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "Repuesto",
                "verbose_name_plural": "Repuestos",
                "ordering": ["nombre"],
            },
        ),
        migrations.CreateModel(
            name="Vehiculo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("placa", models.CharField(max_length=10, unique=True, validators=[taller.validators.validar_placa])),
                ("marca", models.CharField(max_length=50)),
                ("modelo", models.CharField(max_length=50)),
                ("anio", models.PositiveIntegerField(validators=[taller.validators.validar_anio])),
                ("color", models.CharField(max_length=30)),
                ("kilometraje", models.PositiveIntegerField(default=0)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="vehiculos",
                        to="taller.cliente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vehículo",
                "verbose_name_plural": "Vehículos",
                "ordering": ["placa"],
            },
        ),
        migrations.CreateModel(
            name="Cita",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField()),
                ("hora", models.TimeField()),
                ("motivo", models.CharField(max_length=200)),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("confirmada", "Confirmada"),
                            ("atendida", "Atendida"),
                            ("cancelada", "Cancelada"),
                        ],
                        default="pendiente",
                        max_length=20,
                    ),
                ),
                ("observaciones", models.TextField(blank=True)),
                (
                    "mecanico",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="citas",
                        to="taller.mecanico",
                    ),
                ),
                (
                    "vehiculo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="citas",
                        to="taller.vehiculo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cita",
                "verbose_name_plural": "Citas",
                "ordering": ["-fecha", "-hora"],
            },
        ),
        migrations.CreateModel(
            name="Diagnostico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descripcion_problema", models.TextField()),
                ("causa", models.TextField()),
                ("solucion_recomendada", models.TextField()),
                ("fecha", models.DateField()),
                (
                    "costo_estimado",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[taller.validators.validar_no_negativo],
                    ),
                ),
                (
                    "cita",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="diagnosticos",
                        to="taller.cita",
                    ),
                ),
            ],
            options={
                "verbose_name": "Diagnóstico",
                "verbose_name_plural": "Diagnósticos",
                "ordering": ["-fecha", "-id"],
            },
        ),
        migrations.CreateModel(
            name="OrdenServicio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descripcion_trabajo", models.TextField()),
                (
                    "cantidad_repuesto",
                    models.PositiveIntegerField(
                        default=1, validators=[taller.validators.validar_mayor_cero]
                    ),
                ),
                (
                    "costo_mano_obra",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[taller.validators.validar_no_negativo],
                    ),
                ),
                (
                    "costo_total",
                    models.DecimalField(
                        decimal_places=2, default=0, editable=False, max_digits=10
                    ),
                ),
                ("fecha_inicio", models.DateField()),
                ("fecha_entrega", models.DateField()),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("en_proceso", "En proceso"),
                            ("finalizada", "Finalizada"),
                        ],
                        default="pendiente",
                        max_length=20,
                    ),
                ),
                (
                    "diagnostico",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ordenes",
                        to="taller.diagnostico",
                    ),
                ),
                (
                    "repuesto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ordenes",
                        to="taller.repuesto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Orden de servicio",
                "verbose_name_plural": "Órdenes de servicio",
                "ordering": ["-fecha_inicio", "-id"],
            },
        ),
    ]
