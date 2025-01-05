from django.db import models
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from propuestas.utils.utils import validate_file_type, simple_unique_file_path


class Sede(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'sede'

    def __str__(self):
        return self.nombre


class Area(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'area'

    def __str__(self):
        return self.nombre



class Idea(models.Model):
    # Opciones para los estados de revisión y ejecución
    ESTADO_REVISION_CHOICES = [
        ('por_revisar', 'Por Revisar'),
        ('revisada_parcialmente', 'Revisada Parcialmente'),
        ('denegada', 'Denegada'),
        ('en_evaluacion_final', 'En Evaluación Final'),
        ('aprobada', 'Aprobada'),
    ]

    ESTADO_EJECUCION_CHOICES = [
        ('pendiente_ejecucion', 'Pendiente de Ejecución'),
        ('en_ejecucion', 'En Ejecución'),
        ('completada', 'Completada'),
    ]

    # Campos principales
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    tipo = models.CharField(max_length=50, choices=[
        ('problema', 'Problema'),
        ('oportunidad', 'Oportunidad'),
        ('reto', 'Reto'),
    ])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)

    # Estados
    estado_revision = models.CharField(
        max_length=50,
        choices=ESTADO_REVISION_CHOICES,
        default='por_revisar'
    )
    estado_ejecucion = models.CharField(
        max_length=50,
        choices=ESTADO_EJECUCION_CHOICES,
        null=True,
        blank=True
    )

    # Indicadores de revisión
    revisada_por_encargado = models.BooleanField(default=False)
    revisada_por_gerente = models.BooleanField(default=False)
    

    class Meta:
        db_table = 'idea'

    def __str__(self):
        return self.titulo



class Calificacion(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    # Calificaciones específicas
    puntuacion_general = models.IntegerField(null=True, blank=True)  # Escala de 1 a 10
    factibilidad = models.IntegerField(null=True, blank=True)  # Escala de 1 a 10
    viabilidad = models.IntegerField(null=True, blank=True)    # Escala de 1 a 10
    impacto = models.IntegerField(null=True, blank=True)       # Escala de 1 a 10

    # Comentarios adicionales
    comentario = models.TextField(blank=True, null=True)

    # Tipo de calificación
    TIPO_CALIFICACION_CHOICES = [
        ('encargado', 'Encargado'),
        ('gerente', 'Gerente'),
    ]
    tipo_calificacion = models.CharField(max_length=20, choices=TIPO_CALIFICACION_CHOICES)

    class Meta:
        db_table = 'calificacion'
        unique_together = ('idea', 'usuario')  # Un usuario solo puede calificar una idea una vez

    def __str__(self):
        return f"{self.usuario} - {self.idea} - General: {self.puntuacion_general}"


###############################################3


class ArchivoAdjunto(models.Model):
    idea = models.ForeignKey(Idea, on_delete = models.CASCADE, related_name="archivos_adjuntos")
    archivo = models.FileField(upload_to = simple_unique_file_path, validators = [validate_file_type])
    fecha_subida = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'archivo_adjunto'
    
    def __str__(self):
        return os.path.basename(self.archivo.name)


    
###############################################