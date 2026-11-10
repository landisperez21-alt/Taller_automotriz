from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "MotorTech Service · Administración"
admin.site.site_title = "MotorTech Service"
admin.site.index_title = "Panel de administración"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("taller.urls")),
]
