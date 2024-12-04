# filters.py
from django_filters import rest_framework as filters
from propuestas.models import Idea
from propuestas.permissions import IsAdminUserType
from django.db.models import Q

class IdeaFilter(filters.FilterSet):
    sede = filters.CharFilter(field_name="sede__nombre", lookup_expr='iexact')
    area = filters.CharFilter(field_name="area__nombre", lookup_expr='iexact')

    usuario = filters.CharFilter(method='filter_usuario_nombre_apellido')

    class Meta:
        model = Idea
        fields = ['sede', 'area', 'usuario']

    def filter_usuario_nombre_apellido(self, queryset, name, value):
        """
        Filtra por nombre y apellido combinados en un solo campo de búsqueda.
        """
        # Divide la búsqueda en palabras clave
        search_terms = value.split()
        # Construye una consulta combinada para cada palabra clave
        query = Q()
        for term in search_terms:
            query &= Q(usuario__nombre__icontains=term) | Q(usuario__apellido__icontains=term)
        
        return queryset.filter(query)