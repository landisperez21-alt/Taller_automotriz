"""Conversores de ruta que limitan los slugs a los módulos/reportes reales."""


class ModuloConverter:
    regex = "clientes|vehiculos|mecanicos|citas|diagnosticos|repuestos|ordenes"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class TipoDocumentoConverter:
    regex = "citas|diagnosticos|ordenes"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
