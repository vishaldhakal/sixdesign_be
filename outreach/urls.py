from django.urls import path
from . import views

urlpatterns = [
    path('unsubscribe/', views.UnsubscribeEmailsList.as_view(), name='unsubscribe-list'),
    path('unsubscribe/<int:pk>/', views.UnsubscribeEmailsDetail.as_view(), name='unsubscribe-detail'),
]
