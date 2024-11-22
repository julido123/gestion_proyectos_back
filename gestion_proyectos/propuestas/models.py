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
    TIPO_CHOICES = [
        ('problema', 'Problema'),
        ('oportunidad', 'Oportunidad'),
        ('reto', 'Reto'),
        # Agregar otros tipos según sea necesario
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')

    class Meta:
        db_table = 'idea'

    def __str__(self):
        return self.titulo


class Calificacion(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    
    # Puntuación general dada por el gerente u otra figura de liderazgo
    puntuacion_general = models.IntegerField(null=True)  # Escala de 1 a 10
    
    # Calificaciones específicas
    factibilidad = models.IntegerField(null=True)  # Escala de 1 a 10
    viabilidad = models.IntegerField(null=True)    # Escala de 1 a 10
    impacto = models.IntegerField(null=True)       # Escala de 1 a 10

    # Comentario adicional
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'calificacion'
        unique_together = ('idea', 'usuario')  # Un usuario solo puede calificar una idea una vez

    def __str__(self):
        return f"{self.usuario} - {self.idea} - General: {self.puntuacion_general}"

    def promedio(self):
        """
        Calcula el promedio de las calificaciones específicas (factibilidad, viabilidad, impacto)
        """
        return (self.factibilidad + self.viabilidad + self.impacto) / 3


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