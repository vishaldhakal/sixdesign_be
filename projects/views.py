from django.shortcuts import render
from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Agenda, Client
from .serializers import ProjectSerializer, AgendaSerializer, ClientSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        return Project.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if request.method not in permissions.SAFE_METHODS and obj.created_by != request.user:
            raise PermissionDenied("You don't have permission to modify this project.")
        return super().check_object_permissions(request, obj)

class AgendaListCreateView(generics.ListCreateAPIView):
    serializer_class = AgendaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'assigned_to', 'status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['deadline', 'created_at', 'priority']

    def get_queryset(self):
        queryset = Agenda.objects.filter(project_id=self.kwargs['project_id'])
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        project = Project.objects.get(pk=self.kwargs['project_id'])
        serializer.save(project=project)

class AgendaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'email']
    ordering_fields = ['created_at', 'name']

class ClientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
