from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectRetrieveUpdateDestroyView,
    AgendaListCreateView,
    AgendaRetrieveUpdateDestroyView,
    ClientListCreateView,
    ClientRetrieveUpdateDestroyView,
)

app_name = 'projects'

urlpatterns = [
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientRetrieveUpdateDestroyView.as_view(), name='client-detail'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(), name='project-detail'),
    path('projects/<int:project_id>/agendas/', AgendaListCreateView.as_view(), name='agenda-list-create'),
    path('agendas/<int:pk>/', AgendaRetrieveUpdateDestroyView.as_view(), name='agenda-detail'),
] 