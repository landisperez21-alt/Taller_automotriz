"""
Configuración de MotorTech Service.

Todos los valores sensibles o dependientes del entorno se leen de variables
de entorno. Para desarrollo se cargan automáticamente desde el archivo `.env`
(ver `.env.example`); no se necesita ninguna librería adicional.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Variables de entorno
# ---------------------------------------------------------------------------
def _cargar_env(ruta: Path) -> None:
    """Carga pares CLAVE=valor de `.env` sin pisar variables ya definidas."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip("\"'"))


def env(clave, defecto=None):
    return os.environ.get(clave, defecto)


def env_bool(clave, defecto=False):
    valor = os.environ.get(clave)
    if valor is None:
        return defecto
    return valor.strip().lower() in {"1", "true", "t", "yes", "y", "si", "sí", "on"}


def env_int(clave, defecto):
    try:
        return int(os.environ.get(clave, defecto))
    except (TypeError, ValueError):
        return defecto


def env_lista(clave, defecto=""):
    return [x.strip() for x in os.environ.get(clave, defecto).split(",") if x.strip()]


_cargar_env(BASE_DIR / ".env")


# ---------------------------------------------------------------------------
# Seguridad básica
# ---------------------------------------------------------------------------
DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = env("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "inseguro-solo-para-desarrollo-local-no-usar-en-produccion"
    else:
        raise ImproperlyConfigured(
            "Define DJANGO_SECRET_KEY en el archivo .env o en el entorno."
        )

ALLOWED_HOSTS = env_lista("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
CSRF_TRUSTED_ORIGINS = env_lista("DJANGO_CSRF_TRUSTED_ORIGINS")

# Ruta del panel de administración (cámbiala en producción).
ADMIN_URL = env("DJANGO_ADMIN_URL", "admin/").strip("/") + "/"


# ---------------------------------------------------------------------------
# Aplicaciones y middleware
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "taller.apps.TallerConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "taller.context_processors.navegacion",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------------------------
# Base de datos: SQLite (por defecto) o MariaDB/MySQL (DB_ENGINE=mysql)
# ---------------------------------------------------------------------------
if env("DB_ENGINE", "sqlite").lower() in {"mysql", "mariadb"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME", "motortech"),
            "USER": env("DB_USER", "root"),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "127.0.0.1"),
            "PORT": env("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / env("DB_NAME_SQLITE", "db.sqlite3"),
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Contraseñas, sesiones y autenticación
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# "Mantener mi cuenta abierta": duración de la sesión persistente (segundos).
SESSION_REMEMBER_SECONDS = env_int("SESSION_REMEMBER_SECONDS", 60 * 60 * 24 * 14)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Límite de intentos fallidos de inicio de sesión (por IP + usuario).
LOGIN_MAX_INTENTOS = env_int("LOGIN_MAX_INTENTOS", 5)
LOGIN_BLOQUEO_SEGUNDOS = env_int("LOGIN_BLOQUEO_SEGUNDOS", 15 * 60)


# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# ---------------------------------------------------------------------------
# Endurecimiento para producción (DEBUG=False)
# ---------------------------------------------------------------------------
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = env_bool("DJANGO_COOKIES_SEGURAS", not DEBUG)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_HSTS_SECONDS = env_int("DJANGO_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
if env_bool("DJANGO_DETRAS_DE_PROXY", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
