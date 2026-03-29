from rest_framework import serializers
from .models import Project, Agenda, Client


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight: used in list views and embedded in ProjectListSerializer."""

    class Meta:
        model = Client
        fields = ('id', 'name', 'email', 'phone', 'status')


class ClientDetailSerializer(serializers.ModelSerializer):
    """Full representation including notes (HTML) and timestamps."""

    class Meta:
        model = Client
        fields = ('id', 'name', 'email', 'phone', 'address', 'status', 'notes',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


# ---------------------------------------------------------------------------
# Agenda
# ---------------------------------------------------------------------------

class AgendaListSerializer(serializers.ModelSerializer):
    """Lightweight: used inside ProjectDetailSerializer and agenda list."""
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Agenda
        fields = ('id', 'title', 'status', 'priority', 'deadline',
                  'assigned_to', 'assigned_to_name')

    def get_assigned_to_name(self, obj):
        # Works both when assigned_to is a User object and when it's None
        if obj.assigned_to_id is None:
            return None
        # Use pre-fetched related if available to avoid extra query
        user = obj.assigned_to
        return f"{user.first_name} {user.last_name}".strip() or user.username


class AgendaDetailSerializer(serializers.ModelSerializer):
    """Full agenda with description (HTML) and write support for assigned_to."""
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Agenda
        fields = ('id', 'project', 'title', 'description', 'status', 'priority',
                  'deadline', 'assigned_to', 'assigned_to_id', 'assigned_to_name',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'project')

    def get_assigned_to_name(self, obj):
        if obj.assigned_to_id is None:
            return None
        user = obj.assigned_to
        return f"{user.first_name} {user.last_name}".strip() or user.username


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight: used in list responses — no HTML blobs, no nested agendas."""
    client_name = serializers.CharField(source='client.name', read_only=True, default=None)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'title', 'status', 'project_type', 'client', 'client_name',
                  'start_date', 'end_date', 'created_by', 'created_by_name',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def get_created_by_name(self, obj):
        u = obj.created_by
        return f"{u.first_name} {u.last_name}".strip() or u.username


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full project with nested agendas and client details."""
    agendas = AgendaListSerializer(many=True, read_only=True)
    client_details = ClientListSerializer(source='client', read_only=True)
    client_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'status', 'project_type',
                  'client', 'client_id', 'client_details',
                  'start_date', 'end_date', 'additional_info',
                  'created_by', 'created_by_name', 'agendas',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def get_created_by_name(self, obj):
        u = obj.created_by
        return f"{u.first_name} {u.last_name}".strip() or u.username