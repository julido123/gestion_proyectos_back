from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from propuestas.models import Idea, Calificacion
from propuestas.serializers import IdeaSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .filters import IdeaFilter
from propuestas.permissions import IsAdminUserType
from django.db.models import Count, Avg, Q

class IdeaCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = IdeaSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(usuario=request.user)  # Pasa el usuario autenticado directamente
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class IdeaListView(generics.ListAPIView):
    queryset = Idea.objects.all()
    serializer_class = IdeaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IdeaFilter
    permission_classes = [IsAdminUserType] 


class IdeasSinCalificarView(APIView):

    def get(self, request, *args, **kwargs):
        usuario = request.user
        # Obtener ideas que no han sido calificadas por el usuario actual
        ideas_sin_calificar = Idea.objects.exclude(
            id__in=Calificacion.objects.filter(usuario=usuario).values_list('idea', flat=True)
        )
        serializer = IdeaSerializer(ideas_sin_calificar, many=True)
        return Response(serializer.data)


class TotalIdeasPorTipoView(APIView):
    def get(self, request):
        total_ideas = Idea.objects.count()
        ideas_por_tipo = Idea.objects.values('tipo').annotate(count=Count('tipo'))
        data = {
            'total': total_ideas,
            'por_tipo': {item['tipo']: item['count'] for item in ideas_por_tipo}
        }
        return Response(data)
    
    

class IdeasPorAreaView(APIView):
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
        data = list(encuestas_sede)
        return Response(data)