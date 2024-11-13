from django.contrib import admin
from .models import Sede, Area, Idea, Calificacion, Prioridad, Estadistica, ArchivoAdjunto

admin.site.register(Sede)
admin.site.register(Area)
admin.site.register(Idea)
admin.site.register(Calificacion)
admin.site.register(Prioridad)
admin.site.register(Estadistica)
admin.site.register(ArchivoAdjunto)
