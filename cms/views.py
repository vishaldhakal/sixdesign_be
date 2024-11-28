from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Tag, Service, Portfolio, Blog
from .serializers import (
    CategorySerializer, TagSerializer, ServiceSerializer,
    PortfolioListSerializer, PortfolioDetailSerializer,
    BlogListSerializer, BlogDetailSerializer
)
import json

# Create your views here.

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

class PortfolioListCreateView(generics.ListCreateAPIView):
    queryset = Portfolio.objects.all().select_related('category').prefetch_related('tags', 'services')
    serializer_class = PortfolioListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        tags = self.request.data.get('tags')
        services = self.request.data.get('services')
        
        if tags:
            try:
                tags = json.loads(tags)
            except:
                tags = []
                
        if services:
            try:
                services = json.loads(services)
            except:
                services = []

        # Handle thumbnail
        thumbnail = self.request.FILES.get('thumbnail')
        
        # Get category from request data
        category = self.request.data.get('category')
        
        instance = serializer.save(
            thumbnail=thumbnail if thumbnail else None,
            category_id=category
        )
        
        if tags:
            instance.tags.set(tags)
        if services:
            instance.services.set(services)

class PortfolioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all().select_related('category').prefetch_related('tags', 'services')
    serializer_class = PortfolioDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def perform_update(self, serializer):
        tags = self.request.data.get('tags')
        services = self.request.data.get('services')
        
        if tags:
            try:
                tags = json.loads(tags)
            except:
                tags = []
                
        if services:
            try:
                services = json.loads(services)
            except:
                services = []

        # Handle thumbnail
        thumbnail = self.request.FILES.get('thumbnail')
        
        instance = serializer.save(
            thumbnail=thumbnail if thumbnail else serializer.instance.thumbnail,
            category_id=self.request.data.get('category')
        )
        
        if tags:
            instance.tags.set(tags)
        if services:
            instance.services.set(services)

class BlogListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.all().select_related('category').prefetch_related('tags')
    serializer_class = BlogListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        tags = self.request.data.get('tags')
        if tags:
            try:
                tags = json.loads(tags)
            except:
                tags = []

        # Handle thumbnail
        thumbnail = self.request.FILES.get('thumbnail')
        
        # Get category from request data
        category = self.request.data.get('category')
        
        instance = serializer.save(
            thumbnail=thumbnail,
            category_id=category  # Explicitly set category_id
        )
        
        if tags:
            instance.tags.set(tags)

class BlogRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all().select_related('category').prefetch_related('tags')
    serializer_class = BlogDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def perform_update(self, serializer):
        tags = self.request.data.get('tags')
        if tags:
            try:
                tags = json.loads(tags)
            except:
                tags = []

        # Handle thumbnail
        thumbnail = self.request.FILES.get('thumbnail')
        
        instance = serializer.save(thumbnail=thumbnail if thumbnail else serializer.instance.thumbnail)
        
        if tags:
            instance.tags.set(tags)
