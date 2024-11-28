from rest_framework import serializers
from .models import Project, Agenda, Client
from accounts.serializers import UserSerializer

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class AgendaSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Agenda
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ProjectSerializer(serializers.ModelSerializer):
    agendas = AgendaSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    client_details = ClientSerializer(source='client', read_only=True)
    client_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)
        return project

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 