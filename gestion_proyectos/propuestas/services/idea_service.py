import os
from django.conf import settings
from django.db import models
from propuestas.models import Calificacion
from django.db.models import Avg


def calcular_calificacion_definitiva(idea):
        calificaciones = Calificacion.objects.filter(idea=idea)
        if not calificaciones.filter(tipo_calificacion='encargado').exists() or not calificaciones.filter(tipo_calificacion='gerente').exists():
            return None
        promedio = calificaciones.filter(tipo_calificacion__in=['encargado', 'gerente']).aggregate(
            promedio_general=models.Avg('puntuacion_general'),
            # promedio_factibilidad=models.Avg('factibilidad'),
            # promedio_viabilidad=models.Avg('viabilidad'),
            # promedio_impacto=models.Avg('impacto'),
        )
        return promedio


def actualizar_estado_revision(idea):
    """
    Actualiza el estado de revisión basado en las calificaciones del encargado y gerente.
    """
    if not idea.revisada_por_encargado and not idea.revisada_por_gerente:
        idea.estado_revision = 'por_revisar'
    elif idea.revisada_por_encargado and not idea.revisada_por_gerente:
        idea.estado_revision = 'revisada_parcialmente'
    elif idea.revisada_por_encargado and idea.revisada_por_gerente:
        # Obtener calificación definitiva
        calificacion_definitiva = calcular_calificacion_definitiva(idea)
        nota_definitiva = calificacion_definitiva["promedio_general"] if calificacion_definitiva else 0
        
        # Actualizar estado de revisión según la nota
        if nota_definitiva >= 8:
            idea.estado_revision = 'aprobada'
            idea.estado_ejecucion = 'pendiente_ejecucion'  # Estado por defecto si está aprobada
        elif 6 <= nota_definitiva < 8:
            idea.estado_revision = 'en_evaluacion_final'
            idea.estado_ejecucion = None  # Limpiar estado de ejecución
        else:  # nota_definitiva < 6
            idea.estado_revision = 'denegada'
            idea.estado_ejecucion = None  # Limpiar estado de ejecución
    idea.save()


def actualizar_estado_ejecucion(idea, nuevo_estado):
    """
    Actualiza el estado de ejecución solo si la idea está aprobada.
    """
    if idea.estado_revision == 'aprobada':
        idea.estado_ejecucion = nuevo_estado
        idea.save()
    else:
        raise ValueError("Solo las ideas aprobadas pueden tener un estado de ejecución.")
