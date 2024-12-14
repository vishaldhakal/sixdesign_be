from rest_framework import serializers
from .models import UnsubscribeEmails

class UnsubscribeEmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnsubscribeEmails
        fields = ['id', 'email', 'reason', 'created_at']
        read_only_fields = ['created_at']
