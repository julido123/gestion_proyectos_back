# filters.py
from django_filters import rest_framework as filters
from propuestas.models import Idea

class IdeaFilter(filters.FilterSet):
    sede = filters.CharFilter(field_name="sede__nombre", lookup_expr='iexact')
    area = filters.CharFilter(field_name="area__nombre", lookup_expr='iexact')

    class Meta:
        model = Idea
        fields = ['sede', 'area']