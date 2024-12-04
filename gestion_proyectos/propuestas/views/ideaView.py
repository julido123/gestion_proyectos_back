from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from propuestas.models import Idea, Calificacion
from propuestas.serializers import IdeaSerializer, IdeaWithCalificationsSerializer, IdeaSinCalificarSerializer, UpdateIdeaSerializer, UpdateCalificacionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .filters import IdeaFilter
from propuestas.permissions import IsAdminUserType
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.generics import GenericAPIView

class IdeaCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:

            # Recuperar datos directamente
            archivos = request.FILES.getlist('archivos[]')  # Recupera la lista de archivos subidos
            data = {
                'titulo': request.data.get('titulo'),
                'descripcion': request.data.get('descripcion'),
                'tipo': request.data.get('tipo'),
                'sede': request.data.get('sede'),
                'area': request.data.get('area'),
                'archivos': archivos  # Incluye los archivos en los datos a validar
            }

            # Serializar los datos
            serializer = IdeaSerializer(data=data, context={'request': request})

            if serializer.is_valid():
                idea = serializer.save(usuario=request.user)  # Guarda la idea
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            print("Errores del serializer:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Ideas Ya calificadas
class IdeaListView(generics.ListAPIView):
    serializer_class = IdeaWithCalificationsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IdeaFilter
    permission_classes = [IsAdminUserType]

    def get_queryset(self):
        # Filtrar ideas con calificaciones y ordenarlas por la puntuación general más alta
        return Idea.objects.filter(calificacion__isnull=False).annotate(
            max_puntuacion_general=models.Max('calificacion__puntuacion_general')
        ).order_by('-max_puntuacion_general')


class IdeasSinCalificarView(GenericAPIView):
    permission_classes = [IsAdminUserType]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IdeaFilter

    def get(self, request, *args, **kwargs):
        usuario = request.user
        # Obtener ideas que no han sido calificadas por el usuario actual y ordenarlas por fecha_creacion
        ideas_sin_calificar = Idea.objects.exclude(
            id__in=Calificacion.objects.filter(usuario=usuario).values_list('idea', flat=True)
        ).order_by('-fecha_creacion')  # Ordenar por fecha_creacion descendente

        # Aplicar filtros
        ideas_sin_calificar = self.filter_queryset(ideas_sin_calificar)

        # Serializar los datos
        serializer = IdeaSinCalificarSerializer(ideas_sin_calificar, many=True)
        return Response(serializer.data)
    
        


class TotalIdeasPorTipoView(APIView):
    permission_classes = [IsAdminUserType]
    def get(self, request):
        total_ideas = Idea.objects.count()
        ideas_por_tipo = Idea.objects.values('tipo').annotate(count=Count('tipo'))
        data = {
            'total': total_ideas,
            'por_tipo': {item['tipo']: item['count'] for item in ideas_por_tipo}
        }
        return Response(data)
    
    

class IdeasPorAreaView(APIView):
    permission_classes = [IsAdminUserType]
    def get(self, request):
        ideas_area = Idea.objects.values('area__nombre', 'tipo').annotate(count=Count('id'))
        data = {}
        for item in ideas_area:
            area = item['area__nombre']
            tipo = item['tipo']
            count = item['count']
            if area not in data:
                data[area] = {'problema': 0, 'oportunidad': 0, 'reto': 0}
            data[area][tipo] = count
        return Response(data)
    

class IdeasPorSedeView(APIView):
    permission_classes = [IsAdminUserType]
    def get(self, request):
        ideas_sede = Idea.objects.values('sede__nombre', 'tipo').annotate(count=Count('id'))
        data = {}
        for item in ideas_sede:
            sede = item['sede__nombre']
            tipo = item['tipo']
            count = item['count']
            if sede not in data:
                data[sede] = {'problema': 0, 'oportunidad': 0, 'reto': 0}
            data[sede][tipo] = count
        return Response(data)
    

class DetalleEncuestasPorSedeView(APIView):
    permission_classes = [IsAdminUserType]

    def get(self, request):
        encuestas_sede = (
            Idea.objects
            .values('sede__nombre')
            .annotate(
                total_ideas=Count('id'),
                problemas=Count('id', filter=Q(tipo='problema')),
                oportunidades=Count('id', filter=Q(tipo='oportunidad')),
                retos=Count('id', filter=Q(tipo='reto')),
                promedio_calificacion=Avg('calificacion__puntuacion_general')
            )
        )

        # Redondear después de obtener los datos
        data = [
            {
                **item,
                'promedio_calificacion': round(item['promedio_calificacion'], 1)
                if item['promedio_calificacion'] is not None else None
            }
            for item in encuestas_sede
        ]

        return Response(data)
    

class UpdateIdeaEstadoView(APIView):
    permission_classes = [IsAdminUserType]
    def patch(self, request, pk):
        
        idea = get_object_or_404(Idea, pk=pk)
        serializer = UpdateIdeaSerializer(idea, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCalificacionView(APIView):
    permission_classes = [IsAdminUserType]
    def patch(self, request, pk):
        
        calificacion = get_object_or_404(Calificacion, pk=pk)
        serializer = UpdateCalificacionSerializer(calificacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)