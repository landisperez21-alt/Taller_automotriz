from django.core.management.base import BaseCommand

from taller.roles import ROLES, asegurar_grupos


class Command(BaseCommand):
    help = "Crea o actualiza los roles del taller (Consulta, Recepción, Taller, Administrador del taller)."

    def handle(self, *args, **options):
        asegurar_grupos()
        for nombre, permisos in ROLES.items():
            self.stdout.write(self.style.SUCCESS(f"✔ {nombre}: {len(permisos)} permisos"))
