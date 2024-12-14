from django.shortcuts import render
from rest_framework import generics
from .models import UnsubscribeEmails
from .serializers import UnsubscribeEmailsSerializer

# Create your views here.

class UnsubscribeEmailsList(generics.ListCreateAPIView):
    queryset = UnsubscribeEmails.objects.all()
    serializer_class = UnsubscribeEmailsSerializer

class UnsubscribeEmailsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnsubscribeEmails.objects.all()
    serializer_class = UnsubscribeEmailsSerializer
