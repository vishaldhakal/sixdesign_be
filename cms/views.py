from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Tag, Service, Portfolio, Blog, Testimonial
from .serializers import (
    CategorySerializer, TagSerializer, ServiceSerializer,
    PortfolioListSerializer, PortfolioDetailSerializer,
    BlogListSerializer, BlogDetailSerializer, TestimonialSerializer
)
import json
from django.http import HttpResponse
from django.core.mail import EmailMessage
from rest_framework.decorators import api_view

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
                # Convert all IDs to integers, skip any invalid ones
                tag_ids = []
                for tag_id in tags:
                    try:
                        tag_ids.append(int(tag_id))
                    except (ValueError, TypeError):
                        continue
            except json.JSONDecodeError:
                tag_ids = []
                
        if services:
            try:
                services = json.loads(services)
                # Convert all IDs to integers, skip any invalid ones
                service_ids = []
                for service_id in services:
                    try:
                        service_ids.append(int(service_id))
                    except (ValueError, TypeError):
                        continue
            except json.JSONDecodeError:
                service_ids = []

        # Handle thumbnail
        thumbnail = self.request.FILES.get('thumbnail')
        
        # Get category from request data
        category = self.request.data.get('category')
        
        instance = serializer.save(
            thumbnail=thumbnail if thumbnail else None,
            category_id=category
        )
        
        if tags:
            instance.tags.set(tag_ids)
        if services:
            instance.services.set(service_ids)

class PortfolioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all().select_related('category').prefetch_related('tags', 'services')
    serializer_class = PortfolioDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def perform_update(self, serializer):
        tags = self.request.data.get('tags')
        services = self.request.data.get('services')
        
        tag_ids = []
        service_ids = []
        
        if tags:
            try:
                tags_data = json.loads(tags)
                tag_ids = [int(tag_id) for tag_id in tags_data if str(tag_id).isdigit()]
            except (json.JSONDecodeError, ValueError, TypeError):
                tag_ids = []
                
        if services:
            try:
                services_data = json.loads(services)
                service_ids = [int(service_id) for service_id in services_data if str(service_id).isdigit()]
            except (json.JSONDecodeError, ValueError, TypeError):
                service_ids = []

        # Handle thumbnail
        thumbnail = self.request.FILES.get('thumbnail')
        
        instance = serializer.save(
            thumbnail=thumbnail if thumbnail else serializer.instance.thumbnail,
            category_id=self.request.data.get('category')
        )
        
        if tag_ids:
            instance.tags.set(tag_ids)
        if service_ids:
            instance.services.set(service_ids)

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

class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    lookup_field = 'id'


@api_view(["POST"])
def ContactFormSubmission(request):
    if request.method == "POST":
        subject = "Inquiry - SixDesign"
        emaill = "SixDesign <info@sixdesign.ca>"
        headers = {'Reply-To': request.POST["email"]}

        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        message = request.POST["message"]

        body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}\n"

        email = EmailMessage(subject, body, emaill, ["team@sixdesign.ca"],reply_to=[email], headers=headers)

        email.send(fail_silently=False)
        
        return HttpResponse("Success")
    else:
        return HttpResponse("Not a POST request")
