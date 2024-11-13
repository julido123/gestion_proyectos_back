from django.db import models
from django.conf import settings


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


class Prioridad(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    nivel_prioridad = models.IntegerField()  # Por ejemplo, una escala de 1 a 5
    usuario_asignador = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'prioridad'

    def __str__(self):
        return f"{self.idea} - Prioridad {self.nivel_prioridad}"


class Estadistica(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE)
    vistas = models.IntegerField(default=0)
    calificaciones_promedio = models.FloatField(default=0.0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'estadistica'

    def __str__(self):
        return f"Estadísticas de {self.idea}"


class ArchivoAdjunto(models.Model):
    TIPO_ARCHIVO_CHOICES = [
        ('foto', 'Foto'),
        ('video', 'Video'),
        ('excel', 'Excel'),
        # Agregar otros tipos según sea necesario
    ]

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='archivos_ideas/')
    tipo_archivo = models.CharField(max_length=50, choices=TIPO_ARCHIVO_CHOICES)

    class Meta:
        db_table = 'archivo_adjunto'

    def __str__(self):
        return f"{self.tipo_archivo} de {self.idea}"
