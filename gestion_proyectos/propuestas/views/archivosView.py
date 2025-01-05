from propuestas.permissions import IsAdminUserType

from django.http import FileResponse
from django.views import View
from propuestas.services.archivo_service import obtener_imagen

# class ImagenesPorIdeaView(APIView):
#     def get(self, request, idea_id, *args, **kwargs):
#         try:
#             # Filtrar los archivos relacionados con una idea
#             archivos = ArchivoAdjunto.objects.filter(idea_id=idea_id)
#             serializer = ArchivoAdjuntoSerializer(archivos, many=True, context={'request': request})
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class ObtenerImagenView(View):
    permission_classes = [IsAdminUserType]

    def get(self, request, ruta):
        ruta_absoluta = obtener_imagen(ruta)
        return FileResponse(open(ruta_absoluta, 'rb'), content_type='image/jpeg')