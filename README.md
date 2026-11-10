# ⚡ MOTORTECH SERVICE | AUTOMOTIVE MANAGEMENT SYSTEM

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/TECHNOLOGY-Automotive-00D4FF?style=for-the-badge&logo=gear&logoColor=white" />
  <img src="https://img.shields.io/badge/STATUS-ACTIVE-success?style=for-the-badge" />
</p>

<p align="center">
  <b>Sistema Integral de Gestión para Talleres Automotrices.</b>
  <br />
  Plataforma web desarrollada en Django para automatizar operaciones, control de stock y reportes.
</p>

---

## ◈ 01. SOBRE EL PROYECTO

**MotorTech Service** es una plataforma web integral desarrollada con Python y Django para automatizar los procesos operativos de un taller automotriz. 

El sistema gestiona desde la recepción del cliente y registro de vehículos hasta la asignación de mecánicos, generación de diagnósticos, control automático de inventario de repuestos y cálculo de costos en las órdenes de servicio. Además, incluye un control de acceso por roles (Jefe/Administrador, Recepción y Taller/Mecánico).

## ◈ 02. TECNOLOGÍAS

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,django,html,css,js,sqlite,git,github" />
</p>

| Tecnología | Aplicación |
|:---|:---|
| Python | Lógica de negocio y procesamiento backend |
| Django | Framework MVC/MTV web |
| HTML5 | Estructura de plantillas |
| CSS3 | Diseño de interfaz adaptativo (CSS custom) |
| JavaScript | Dinamismo y actualización automática |
| SQLite | Base de datos relacional predeterminada |
| Git & GitHub | Control de versiones |

## ◈ 03. ESTRUCTURA DEL PROYECTO

```text
Taller_automotriz-main/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── taller/
│   ├── forms/
│   ├── management/
│   │   └── commands/ (cargar_demo, crear_roles)
│   ├── migrations/
│   ├── models/ (cliente, vehiculo, cita, diagnostico, mecanico, orden_servicio, repuesto)
│   ├── static/taller/ (css, js)
│   ├── templates/ (crud, reportes, registration)
│   ├── views/
│   ├── admin.py
│   └── urls.py
│
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
## ◈ 04. INSTALACIÓN Y EJECUCIÓN

Clona el repositorio:

```
git clone [https://github.com/landisperez21-alt/Taller_automotriz.git](https://github.com/landisperez21-alt/Taller_automotriz.git)
Ingresa al directorio del proyecto:Bashcd Taller_automotriz
Crea un entorno virtual:
```
python -m venv .venv
Actívalo en Windows (PowerShell):PowerShell.venv\Scripts\activate
Instala las dependencias:
```
pip install -r requirements.txt
Ejecuta las migraciones:
```
python manage.py migrate
Carga los datos de demostración y cuentas demo:
```
python manage.py cargar_demo --usuarios
Inicia el servidor local:Bashpython manage.py runserver
Abre el navegador en: 
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## ◈5. PROPÓSITO
Automatizar el flujo operativo completo de un taller automotriz. 
Implementar control de permisos granular según el rol del usuario.
Gestionar el stock de repuestos dinámicamente con cada orden de servicio.   
Generar reportes imprimibles y exportables en formato PDF desde el navegador.   

## ◈ 06. AUTOR

<table>
<tr>
<td>
<strong>Landis Sanchez Perez</strong><br/>
Desarrollador de software | Tecnología IoT<br/><br/>
<a href="https://github.com/landisperez21">
<img src="https://img.shields.io/badge/GitHub-landisperez21-181717?style=flat-square&logo=github" />
</a>
</td>
</tr>
</table>

---

<p align="center">
  <b>BUILDING IDEAS THROUGH TECHNOLOGY.</b>
  <br/>
  <sub>Software · Electronics · Internet of Things</sub>
</p>
