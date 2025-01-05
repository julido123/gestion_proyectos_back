# services/file_service.py
import os
from django.conf import settings
from django.http import Http404

def obtener_imagen(ruta):
    ruta_absoluta = os.path.join(settings.MEDIA_ROOT, ruta)
    if os.path.exists(ruta_absoluta):
        return ruta_absoluta
    raise Http404("Imagen no encontrada")