from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Website, Activity, People
from .serializers import (
    WebsiteSerializer, 
    ActivitySerializer, 
    TrackingEventSerializer,
    PeopleSerializer
)
from django.shortcuts import get_object_or_404
import json
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db import models

class WebsiteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WebsiteSerializer

    def get_queryset(self):
        return Website.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def track_event(request):
    serializer = TrackingEventSerializer(data=request.data)
    if serializer.is_valid():
        site_id = serializer.validated_data['site_id']
        website = get_object_or_404(Website, site_id=site_id)
        
        # Get visitor identification data
        visitor_id = serializer.validated_data.get('visitor_id')
        visitor_email = serializer.validated_data.get('visitor_email')
        form_data = serializer.validated_data.get('form_data', {})
        
        # Try to identify the user
        email = form_data.get('email') or visitor_email
        
        # Only proceed if we have an email to identify the user
        if email:
            # Try to find or create the person
            name = form_data.get('name')
            phone = form_data.get('phone')
            
            # Update or create person with all available identifiers
            person, created = People.objects.update_or_create(
                email=email,
                defaults={
                    'name': name or email.split('@')[0],
                    'phone': phone or '',
                    'visitor_id': visitor_id,
                    'user_agent': serializer.validated_data.get('user_agent'),
                    'language': serializer.validated_data.get('language'),
                    'screen_resolution': serializer.validated_data.get('screen_resolution'),
                    'timezone': serializer.validated_data.get('timezone'),
                }
            )
            
            # Create activity for identified user
            Activity.objects.create(
                website=website,
                people=person,
                activity_type=serializer.validated_data['event_type'],
                page_title=serializer.validated_data.get('page_title'),
                page_url=serializer.validated_data.get('page_url'),
                page_referrer=serializer.validated_data.get('page_referrer') or None,
                page_duration=serializer.validated_data.get('page_duration'),
                form_data=form_data,
                metadata=serializer.validated_data.get('metadata'),
                visitor_id=visitor_id,
                user_agent=serializer.validated_data.get('user_agent'),
                language=serializer.validated_data.get('language'),
                screen_resolution=serializer.validated_data.get('screen_resolution'),
                timezone=serializer.validated_data.get('timezone')
            )
            
            return Response({'status': 'success', 'identified': True})
        
        return Response({'status': 'skipped', 'reason': 'unidentified_user'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def dashboard_stats(request):
    now = timezone.now()
    online_threshold = now - timedelta(minutes=1)
    
    online_visitors = Activity.objects.filter(
        last_heartbeat__gte=online_threshold
    ).values('people').distinct().count()
    
    total_visits = Activity.objects.filter(activity_type='Viewed Page').count()
    total_people = People.objects.count()
    
    recent_activities = Activity.objects.select_related('people', 'website')\
        .exclude(activity_type='Heartbeat')\
        .order_by('-occured_at')[:10]
    
    online_people = People.objects.filter(
        activity__last_heartbeat__gte=online_threshold
    ).distinct()
    
    return Response({
        'totalVisits': total_visits,
        'totalPeople': total_people,
        'onlineVisitors': online_visitors,
        'recentActivities': ActivitySerializer(recent_activities, many=True).data,
        'onlinePeople': PeopleSerializer(online_people, many=True).data
    })

@api_view(['GET'])
def people_list(request):
    now = timezone.now()
    online_threshold = now - timedelta(minutes=1)
    
    people = People.objects.annotate(
        is_online=models.Exists(
            Activity.objects.filter(
                people=models.OuterRef('pk'),
                last_heartbeat__gte=online_threshold
            )
        )
    ).order_by('-last_activity')
    
    return Response(PeopleSerializer(people, many=True).data)

@api_view(['GET'])
def person_detail(request, pk):
    person = get_object_or_404(People, pk=pk)
    return Response(PeopleSerializer(person).data)

@api_view(['GET'])
def person_activities(request, pk):
    activities = Activity.objects.filter(people_id=pk).order_by('-occured_at')
    return Response(ActivitySerializer(activities, many=True).data)
