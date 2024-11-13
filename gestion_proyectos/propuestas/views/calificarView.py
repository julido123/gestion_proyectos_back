from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from propuestas.models import Calificacion, Idea
from propuestas.serializers import CalificacionSerializer
from accounts.models import Account
from propuestas.permissions import IsAdminUserType

class CalificacionCreateView(APIView):
    permission_classes = [IsAdminUserType] 

    def post(self, request, *args, **kwargs):
        try:
            # Obtener datos directamente del JSON, excepto el usuario
            idea_id = request.data.get('idea')
            factibilidad = request.data.get('factibilidad')
            viabilidad = request.data.get('viabilidad')
            impacto = request.data.get('impacto')
            comentario = request.data.get('comentario', '')
            puntuacion_general = request.data.get('puntuacion_general', '')

            # Validar y obtener la instancia de Idea
            idea = Idea.objects.get(id=idea_id)

            # Obtener el usuario autenticado desde el token
            usuario = request.user

            # Crear la calificación
            calificacion = Calificacion.objects.create(
                idea=idea,
                usuario=usuario,
                factibilidad=int(factibilidad),
                viabilidad=int(viabilidad),
                impacto=int(impacto),
                comentario=comentario,
                puntuacion_general=puntuacion_general
            )

            # Cambiar el estado de la idea a 'en_progreso'
            idea.estado = 'en_progreso'
            idea.save()  # Guarda los cambios en la base de datos

            # Serializar la calificación y devolver la respuesta
            serializer = CalificacionSerializer(calificacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Idea.DoesNotExist:
            return Response({"error": "Idea no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": f"Valor inválido: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
