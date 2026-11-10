# Guía de sustentación técnica

| Tema | Dónde verlo | Qué explicar |
|---|---|---|
| Modelos | `taller/models/*.py` | Una clase por archivo; `__init__.py` las exporta. Validadores en `taller/validators.py`. |
| Relaciones | `docs/diagrama_er.png` | Cliente 1‑N Vehículo · Vehículo 1‑N Cita · Mecánico 1‑N Cita · Cita 1‑N Diagnóstico · Diagnóstico 1‑N Orden · Repuesto 1‑N Orden. `on_delete=PROTECT` conserva el historial. |
| Migraciones | `taller/migrations/0001_initial.py` | Crea las 7 tablas; tras `migrate` se crean los roles (`post_migrate` en `apps.py`). |
| Formularios | `taller/forms/` | `TallerBaseForm` (estilos, fecha/hora nativas) + validaciones: DNI 8 dígitos, placa, año, stock, choque de horario, fechas coherentes. |
| Vistas | `taller/views/` | `web.py`: login, registro, dashboard, reportes, documentos · `crud.py`: 4 vistas genéricas para los 7 módulos. |
| Rutas | `taller/urls.py`, `taller/converters.py` | Rutas fijas primero; luego `<modulo:slug>/`, `nuevo/`, `<pk>/editar/`, `<pk>/eliminar/`. Los conversores limitan los slugs válidos. |
| Registro de módulos | `taller/modulos.py` | Define columnas, búsqueda e iconos de cada módulo; alimenta CRUD, menú y permisos. |
| Plantillas | `taller/templates/` | `base.html` hereda a todas; `crud/`, `reportes/`, `components/`. |
| Autenticación | `forms/auth.py`, `views/web.py`, `roles.py` | «Mantener mi cuenta abierta» con `set_expiry`; registro sin `is_staff`/`is_superuser`; límite de intentos fallidos. |
| Reportes | `views/web.py`, `reportes/*.html`, `components.css` (`@media print`) | Filtros con ORM; impresión/PDF del navegador. |
| Dashboard | `views/web.py` (`calcular_kpis`), `app.js` | `count()`/`Sum()`; `/api/kpis/` refresca cada 30 s. |

## Guion de demostración (5 min)
1. Login con y sin «Mantener mi cuenta abierta»; registro de un usuario nuevo (solo consulta).
2. Dashboard: KPIs, barras por estado, ingresos.
3. Flujo: cliente → vehículo → cita → diagnóstico → orden (total en vivo, stock bajando).
4. Búsqueda y filtro por estado; intentar borrar un cliente con vehículos.
5. Reportes: filtrar órdenes → Imprimir → Guardar como PDF; documento de una orden.
6. Entrar como `recepcion_demo`: no ve Órdenes ni puede eliminar.
