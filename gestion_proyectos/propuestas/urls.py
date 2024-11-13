from django.urls import path
from propuestas.views.ideaView import IdeaCreateView, IdeaListView, IdeasSinCalificarView, TotalIdeasPorTipoView, IdeasPorAreaView, IdeasPorSedeView, DetalleEncuestasPorSedeView
from propuestas.views.calificarView import CalificacionCreateView
from propuestas.views.rankingView import UserRankingView
from propuestas.views.sedeView import SedeListView
from propuestas.views.areaView import AreaListView



urlpatterns = [
    path('crear-idea/', IdeaCreateView.as_view(), name='crear_idea_api'),
    path('listar-ideas/', IdeaListView.as_view(), name='idea-list'),
    path('calificar-idea/', CalificacionCreateView.as_view(), name='calificar-idea'),
    path('ranking-ideas/', UserRankingView.as_view(), name='ranking-usuarios'),
    path('sedes/', SedeListView.as_view(), name='sedes-list'),
    path('areas/', AreaListView.as_view(), name='areas-list'),
    path('ideas-sin-calificar/', IdeasSinCalificarView.as_view(), name='ideas-sin-calificar'),
    
    
    path('total-ideas-por-tipo/', TotalIdeasPorTipoView.as_view(), name='total_ideas_por_tipo'),
    path('ideas-por-area/', IdeasPorAreaView.as_view(), name='ideas_por_area'),
    path('ideas-por-sede/', IdeasPorSedeView.as_view(), name='ideas_por_sede'),
    path('detalle-encuestas-por-sede/', DetalleEncuestasPorSedeView.as_view(), name='detalle_encuestas_por_sede'),
]