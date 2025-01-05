from propuestas.serializers import AreaSerializer
from propuestas.models import Area
from rest_framework import generics
from propuestas.permissions import IsAdminUserType


class AreaListView(generics.ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
