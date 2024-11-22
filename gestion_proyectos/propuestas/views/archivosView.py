from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from propuestas.models import ArchivoAdjunto
from propuestas.serializers import ArchivoAdjuntoSerializer

class ImagenesPorIdeaView(APIView):
    def get(self, request, idea_id, *args, **kwargs):
        try:
            # Filtrar los archivos relacionados con una idea
            archivos = ArchivoAdjunto.objects.filter(idea_id=idea_id)
            serializer = ArchivoAdjuntoSerializer(archivos, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
