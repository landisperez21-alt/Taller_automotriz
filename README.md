⚡ MOTORTECH SERVICE | AUTOMOTIVE MANAGEMENT SYSTEM◈ 01. SOBRE EL PROYECTOMotorTech Service es una plataforma web desarrollada con Python y Django para automatizar los procesos operativos de un taller automotriz.El sistema gestiona la recepción de clientes, registro de vehículos, asignación de mecánicos, generación de diagnósticos, control automático de inventario de repuestos y cálculo de costos en las órdenes de servicio, incorporando control de acceso por roles (Jefe/Administrador, Recepción y Taller/Mecánico).◈ 02. TECNOLOGÍASTecnologíaAplicaciónPythonLógica de negocio y procesamiento backendDjangoFramework web MVC / MTVHTML5Estructura de plantillas HTMLCSS3Diseño de interfaz adaptativo (CSS propio)JavaScriptInteracción dinámica y actualización de datosSQLiteBase de datos relacional de desarrolloGit & GitHubControl de versiones◈ 03. ESTRUCTURA DEL PROYECTOTaller_automotriz-main/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── taller/
│   ├── forms/
│   ├── management/commands/ (cargar_demo, crear_roles)
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
◈ 04. INSTALACIÓNClona el repositorio:git clone https://github.com/landisperez21-alt/Taller_automotriz.git
Ingresa al directorio del proyecto:cd Taller_automotriz
Crea un entorno virtual:python -m venv .venv
Actívalo en Windows:.venv\Scripts\activate
Instala las dependencias:pip install -r requirements.txt
Ejecuta las migraciones:python manage.py migrate
Carga los datos de demostración y cuentas demo:python manage.py cargar_demo --usuarios
Inicia el servidor:python manage.py runserver
Abre el navegador:http://127.0.0.1:8000/
Credenciales de prueba creadas:Administrador: jefe_demo | demo1234Recepción: recepcion_demo | demo1234Taller / Mecánico: taller_demo | demo1234◈ 05. PROPÓSITOAutomatizar el flujo operativo completo de un taller automotriz.Implementar un control de permisos granular según el rol del usuario.Gestionar el stock de repuestos dinámicamente con cada orden de servicio.Generar reportes imprimibles y exportables en formato PDF desde el navegador.
◈ 06. AUTOR
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
