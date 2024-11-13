# views.py
from django.db.models import Count, Avg
from rest_framework import generics
from rest_framework.response import Response
from propuestas.models import Idea, Calificacion
from accounts.models import Account
from propuestas.serializers import AccountRankingSerializer

class UserRankingView(generics.ListAPIView):
    serializer_class = AccountRankingSerializer

    def get_queryset(self):
        # Anotamos la cantidad de ideas y el promedio de `puntuacion_general`
        # y excluimos a los usuarios que no tienen ideas (total_ideas = 0)
        return Account.objects.annotate(
            total_ideas=Count('idea'),
            promedio_calificacion=Avg('idea__calificacion__puntuacion_general')
        ).filter(total_ideas__gt=0).order_by('-total_ideas', '-promedio_calificacion')
