from propuestas.serializers import SedeSerializer
from propuestas.models import Sede
from rest_framework import generics


class SedeListView(generics.ListAPIView):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer

