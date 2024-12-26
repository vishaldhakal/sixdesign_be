from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from activity.views import (
    WebsiteViewSet, track_event, dashboard_stats,
    people_list, person_detail, person_activities
)

router = DefaultRouter()
router.register(r'websites', WebsiteViewSet, basename='website')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('expense.urls')),
    path('api/track/', track_event, name='track-event'),
    path('api/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('api/people/', people_list, name='people-list'),
    path('api/people/<int:pk>/', person_detail, name='person-detail'),
    path('api/people/<int:pk>/activities/', person_activities, name='person-activities'),
    path('api/cms/', include('cms.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('api/outreach/', include('outreach.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/urls/', include('django.contrib.admindocs.urls')),
    ]