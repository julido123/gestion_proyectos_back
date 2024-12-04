from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Avg, Count
from accounts.models import Account
from propuestas.models import Idea, Calificacion

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Extraer el usuario autenticado desde el token
        user = request.user
        
        # Datos básicos del usuario
        nombre = user.nombre
        username = user.username
        apellido = user.apellido
        cedula = user.cedula
        user_type = user.user_type

        # Contar la cantidad de ideas creadas por el usuario
        cantidad_ideas = Idea.objects.filter(usuario=user).count()

        # Calcular el promedio de calificaciones generales de las ideas
        promedio_calificacion = Calificacion.objects.filter(idea__usuario=user).aggregate(
            promedio_general=Avg('puntuacion_general')
        )['promedio_general']

        # En caso de que no haya calificaciones aún, asignar None
        promedio_calificacion = promedio_calificacion if promedio_calificacion is not None else 0

        # Crear la respuesta
        data = {
            'nombre': nombre,
            'apellido': apellido,
            'nombre_usuario': username,
            'user_type': user_type,
            'cedula': cedula,
            'cantidad_ideas': cantidad_ideas,
            'promedio_calificacion': round(promedio_calificacion, 2)
        }

        return Response(data, status=200)
