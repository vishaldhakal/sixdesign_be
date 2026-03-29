from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Agenda, Client
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    AgendaListSerializer, AgendaDetailSerializer,
    ClientListSerializer, ClientDetailSerializer,
)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class ClientListCreateView(generics.ListCreateAPIView):
    """
    GET  — .values() for cheap list response (no model instantiation).
    POST — full queryset so model logic runs correctly.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'email']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return Client.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return ClientListSerializer

    def list(self, request, *args, **kwargs):
        # .values() path: skip model instantiation entirely for list GET
        qs = self.filter_queryset(self.get_queryset())
        data = list(qs.values('id', 'name', 'email', 'phone', 'status'))
        return Response(data)


class ClientRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'project_type', 'created_by']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'end_date']

    def get_serializer_class(self):
        return ProjectListSerializer

    def get_queryset(self):
        # select_related joins exactly what ProjectListSerializer needs —
        # client.name and created_by.first_name/last_name/username
        return (
            Project.objects
            .select_related('client', 'created_by')
            .only(
                'id', 'title', 'status', 'project_type',
                'start_date', 'end_date', 'created_at', 'updated_at',
                # FK ids are implicit; join columns:
                'client__id', 'client__name',
                'created_by__id', 'created_by__first_name',
                'created_by__last_name', 'created_by__username',
            )
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Full model + prefetch agendas with their assigned users
        return (
            Project.objects
            .select_related('client', 'created_by')
            .prefetch_related('agendas__assigned_to')
        )

    def check_object_permissions(self, request, obj):
        if request.method not in permissions.SAFE_METHODS and obj.created_by != request.user:
            raise PermissionDenied("You don't have permission to modify this project.")
        return super().check_object_permissions(request, obj)


# ---------------------------------------------------------------------------
# Agenda
# ---------------------------------------------------------------------------

class AgendaListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to']
    search_fields = ['title']
    ordering_fields = ['deadline', 'created_at', 'priority']

    def get_serializer_class(self):
        return AgendaListSerializer

    def get_queryset(self):
        return (
            Agenda.objects
            .filter(project_id=self.kwargs['project_id'])
            .select_related('assigned_to')
            .only(
                'id', 'title', 'status', 'priority', 'deadline',
                'assigned_to__id', 'assigned_to__first_name',
                'assigned_to__last_name', 'assigned_to__username',
            )
        )

    def perform_create(self, serializer):
        project = Project.objects.only('id').get(pk=self.kwargs['project_id'])
        serializer.save(project=project)


class AgendaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AgendaDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Agenda.objects.select_related('assigned_to', 'project')
