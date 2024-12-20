from rest_framework import serializers
from .models import Website, Activity, People, Tag

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['id', 'name', 'site_id', 'tracking_code', 'domain', 'created_at']
        read_only_fields = ['site_id', 'tracking_code']

class PeopleSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = People
        fields = [
            'id', 'name', 'email', 'phone', 'last_activity', 
            'stage', 'source', 'source_url', 'created_at',
            'is_online'
        ]

class ActivitySerializer(serializers.ModelSerializer):
    website = WebsiteSerializer()
    people = PeopleSerializer()
    
    class Meta:
        model = Activity
        fields = '__all__'

class TrackingEventSerializer(serializers.Serializer):
    site_id = serializers.CharField()
    event_type = serializers.CharField()
    page_title = serializers.CharField(required=False, allow_null=True)
    page_url = serializers.URLField(required=False, allow_null=True)
    page_referrer = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    page_duration = serializers.IntegerField(required=False, allow_null=True)
    form_data = serializers.JSONField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False, allow_null=True)
    visitor_id = serializers.CharField(required=False, allow_null=True)
    visitor_email = serializers.EmailField(required=False, allow_null=True)
    user_agent = serializers.CharField(required=False, allow_null=True)
    language = serializers.CharField(required=False, allow_null=True)
    screen_resolution = serializers.CharField(required=False, allow_null=True)
    timezone = serializers.CharField(required=False, allow_null=True) 