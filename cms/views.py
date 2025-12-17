from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Tag, Service, Portfolio, Blog, Testimonial
from .serializers import (
    CategorySerializer, TagSerializer, ServiceSerializer,
    PortfolioListSerializer, PortfolioDetailSerializer,
    BlogListSerializer, BlogDetailSerializer, TestimonialSerializer
)
import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests

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
            except (json.JSONDecodeError, ValueError, TypeError):
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
            except (json.JSONDecodeError, ValueError, TypeError):
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
        name = request.data.get("name")
        email = request.data.get("email")
        phone = request.data.get("phone")
        message = request.data.get("message")

        missing_fields = [field for field, value in {
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
        }.items() if not value]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        api_key = getattr(settings, "EMAIL_HOST_PASSWORD", "") or os.getenv("RESEND_APIKEY", "")
        if not api_key:
            return Response(
                {"error": "Missing RESEND_APIKEY"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        subject = "Inquiry - SixDesign"
        sender = "SixDesign <info@sixdesign.ca>"
        recipient = "team@sixdesign.ca"

        html_body = f"""
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Message:</strong><br>{message}</p>
        """

        payload = {
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "html": html_body,
            "reply_to": [email] if email else []
        }

        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10,
            )
            if resp.ok:
                return Response({"message": "Success"}, status=status.HTTP_200_OK)

            error_body = None
            try:
                error_body = resp.json()
            except ValueError:
                error_body = resp.text

            return Response(
                {"error": "Failed to send", "details": error_body},
                status=resp.status_code,
            )
        except requests.RequestException as exc:
            return Response(
                {"error": "Failed to send", "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    return Response({"error": "Not a POST request"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
