from propuestas.permissions import IsAdminUserType

from django.http import HttpResponse, Http404
from django.conf import settings
import os
from django.views import View

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
        """
        Maneja una solicitud GET para devolver una imagen desde el directorio media.
        :param request: La solicitud HTTP
        :param ruta: La ruta relativa del archivo en el directorio media
        :return: HttpResponse con el contenido de la imagen o un error 404 si no se encuentra
        """
        # Construye la ruta completa del archivo   
        ruta_absoluta = os.path.join(settings.MEDIA_ROOT, ruta)

        # Verifica si el archivo existe
        if os.path.exists(ruta_absoluta):
            # Abre y devuelve la imagen
            with open(ruta_absoluta, 'rb') as archivo:
                return HttpResponse(archivo.read(), content_type='image/jpeg')  # Cambia el content_type según el formato
        else:
            raise Http404("Imagen no encontrada")
