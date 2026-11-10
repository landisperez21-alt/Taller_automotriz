from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _crear_roles(sender, **kwargs):
    from taller.roles import asegurar_grupos

    asegurar_grupos()


class TallerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "taller"
    verbose_name = "MotorTech Service"

    def ready(self):
        # Tras cada `migrate` se crean/actualizan los roles del taller.
        post_migrate.connect(_crear_roles, sender=self)
