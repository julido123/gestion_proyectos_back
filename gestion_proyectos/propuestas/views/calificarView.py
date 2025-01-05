from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from propuestas.models import Calificacion, Idea
from propuestas.serializers import CalificacionSerializer
from propuestas.permissions import IsAdminUserType
from propuestas.services.idea_service import actualizar_estado_ejecucion, actualizar_estado_revision

class CalificacionCreateView(APIView):
    permission_classes = [IsAdminUserType]

    def post(self, request, *args, **kwargs):
        try:
            # Obtener datos del JSON
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

            # Determinar el tipo de calificación según el rol del usuario
            if hasattr(usuario, 'area_encargada') and usuario.area_encargada:
                if idea.area != usuario.area_encargada:
                    return Response(
                        {"error": "No tienes permiso para calificar ideas de esta área"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                tipo_calificacion = 'encargado'
                idea.revisada_por_encargado = True

            elif usuario.es_gerente:
                tipo_calificacion = 'gerente'
                idea.revisada_por_gerente = True
            else:
                return Response(
                    {"error": "No tienes el rol adecuado para calificar esta idea"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Crear la calificación
            calificacion = Calificacion.objects.create(
                idea=idea,
                usuario=usuario,
                factibilidad=int(factibilidad),
                viabilidad=int(viabilidad),
                impacto=int(impacto),
                comentario=comentario,
                puntuacion_general=puntuacion_general,
                tipo_calificacion=tipo_calificacion
            )

            # Actualizar estados de la idea
            actualizar_estado_revision(idea)

            # Si la idea está aprobada, establecer el estado de ejecución predeterminado
            

            # Serializar la calificación y devolver la respuesta
            serializer = CalificacionSerializer(calificacion)
            
            print(idea.estado_revision, "++++--")
            if idea.estado_revision == 'aprobada':
                actualizar_estado_ejecucion(idea, 'pendiente_ejecucion')
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Idea.DoesNotExist:
            return Response({"error": "Idea no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": f"Valor inválido: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
