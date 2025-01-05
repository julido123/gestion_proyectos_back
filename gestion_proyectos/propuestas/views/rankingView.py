# views.py
from django.db.models import Count, Avg, Q
from rest_framework import generics
from accounts.models import Account
from propuestas.serializers import AccountRankingSerializer
from datetime import timedelta
from django.utils.timezone import now
from propuestas.permissions import IsAdminUserType

class UserRankingView(generics.ListAPIView):
    # permission_classes = [IsAdminUserType]
    serializer_class = AccountRankingSerializer

    def get_queryset(self):
        # Obtener el parámetro de tiempo de la consulta ('period') 
        period = self.request.query_params.get('period', 'all')  # Valor predeterminado: 'all'

        # Calcular la fecha de inicio según el período
        if period == 'week':  # Última semana
            start_date = now() - timedelta(weeks=1)
        elif period == 'month':  # Último mes
            start_date = now() - timedelta(days=30)
        else:  # 'all' o cualquier otro valor, sin filtro de tiempo
            start_date = None

        # Construir el filtro temporal
        date_filter = Q()
        if start_date:
            date_filter = Q(idea__fecha_creacion__gte=start_date)

        # Anotación, filtro y ordenamiento
        return Account.objects.annotate(
            total_ideas=Count('idea', filter=date_filter),
            promedio_calificacion=Avg('idea__calificacion__puntuacion_general', filter=date_filter)
        ).filter(
            total_ideas__gt=0,
            promedio_calificacion__isnull=False  # Excluir usuarios sin calificaciones
        ).order_by('-promedio_calificacion', '-total_ideas')