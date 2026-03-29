import json

from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import requests

from .models import Category, Tag, Service, Portfolio, Blog, Testimonial
from .serializers import (
    CategorySerializer, TagSerializer, ServiceSerializer,
    PortfolioListSerializer, PortfolioDetailSerializer,
    BlogListSerializer, BlogDetailSerializer,
    TestimonialSerializer,
)


# ---------------------------------------------------------------------------
# Category / Tag / Service — tiny tables, .values() list for free
# ---------------------------------------------------------------------------

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        data = list(Category.objects.values('id', 'name'))
        return Response(data)


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'


class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        data = list(Tag.objects.values('id', 'name'))
        return Response(data)


class TagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        data = list(Service.objects.values('id', 'name', 'description'))
        return Response(data)


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

class PortfolioListCreateView(generics.ListCreateAPIView):
    serializer_class = PortfolioListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Portfolio.objects
            .select_related('category')
            .prefetch_related('tags')
            .only('id', 'name', 'slug', 'thumbnail', 'link', 'created_at',
                  'category__id', 'category__name')
        )

    def perform_create(self, serializer):
        tag_ids = self._parse_int_list(self.request.data.get('tags'))
        service_ids = self._parse_int_list(self.request.data.get('services'))
        thumbnail = self.request.FILES.get('thumbnail')
        category = self.request.data.get('category')

        instance = serializer.save(
            thumbnail=thumbnail or None,
            category_id=category,
        )
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        if service_ids is not None:
            instance.services.set(service_ids)

    @staticmethod
    def _parse_int_list(raw):
        """Parse a JSON-encoded list of IDs from multipart form data."""
        if not raw:
            return None
        try:
            items = json.loads(raw) if isinstance(raw, str) else raw
            return [int(i) for i in items if str(i).isdigit()]
        except (json.JSONDecodeError, TypeError, ValueError):
            return []


class PortfolioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Portfolio.objects
            .select_related('category')
            .prefetch_related('tags', 'services')
        )

    def perform_update(self, serializer):
        tag_ids = PortfolioListCreateView._parse_int_list(self.request.data.get('tags'))
        service_ids = PortfolioListCreateView._parse_int_list(self.request.data.get('services'))
        thumbnail = self.request.FILES.get('thumbnail')

        instance = serializer.save(
            thumbnail=thumbnail if thumbnail else serializer.instance.thumbnail,
            category_id=self.request.data.get('category'),
        )
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        if service_ids is not None:
            instance.services.set(service_ids)


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

class BlogListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Blog.objects
            .select_related('category')
            .only('id', 'title', 'slug', 'short_description', 'thumbnail',
                  'created_at', 'category__id', 'category__name')
        )

    def perform_create(self, serializer):
        tag_ids = self._parse_tags(self.request.data.get('tags'))
        thumbnail = self.request.FILES.get('thumbnail')
        category = self.request.data.get('category')

        instance = serializer.save(thumbnail=thumbnail, category_id=category)
        if tag_ids:
            instance.tags.set(tag_ids)

    @staticmethod
    def _parse_tags(raw):
        if not raw:
            return []
        try:
            return json.loads(raw) if isinstance(raw, str) else list(raw)
        except (json.JSONDecodeError, TypeError):
            return []


class BlogRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BlogDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Blog.objects
            .select_related('category')
            .prefetch_related('tags')
        )

    def perform_update(self, serializer):
        tag_ids = BlogListCreateView._parse_tags(self.request.data.get('tags'))
        thumbnail = self.request.FILES.get('thumbnail')

        instance = serializer.save(
            thumbnail=thumbnail if thumbnail else serializer.instance.thumbnail
        )
        if tag_ids:
            instance.tags.set(tag_ids)


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------

class TestimonialListCreateView(generics.ListCreateAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Testimonial.objects.only(
            'id', 'name', 'position', 'title', 'description', 'avatar', 'rating', 'created_at'
        )


class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    lookup_field = 'id'


# ---------------------------------------------------------------------------
# Contact form (external Resend API, no DB touch)
# ---------------------------------------------------------------------------

@api_view(["POST"])
def ContactFormSubmission(request):
    name = request.data.get("name")
    email = request.data.get("email")
    phone = request.data.get("phone")
    message = request.data.get("message")

    missing = [k for k, v in {"name": name, "email": email, "phone": phone, "message": message}.items() if not v]
    if missing:
        return Response(
            {"error": f"Missing required fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    api_key = getattr(settings, "EMAIL_HOST_PASSWORD", "") or __import__('os').getenv("RESEND_APIKEY", "")
    if not api_key:
        return Response({"error": "Missing RESEND_APIKEY"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    html_body = (
        f"<p><strong>Name:</strong> {name}</p>"
        f"<p><strong>Email:</strong> {email}</p>"
        f"<p><strong>Phone:</strong> {phone}</p>"
        f"<p><strong>Message:</strong><br>{message}</p>"
    )

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "from": "SixDesign <info@sixdesign.ca>",
                "to": ["team@sixdesign.ca"],
                "subject": "Inquiry — SixDesign",
                "html": html_body,
                "reply_to": [email],
            },
            timeout=(5, 10),
        )
        if resp.ok:
            return Response({"message": "Success"}, status=status.HTTP_200_OK)

        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        return Response({"error": "Failed to send", "details": detail}, status=resp.status_code)

    except requests.Timeout:
        return Response({"error": "Request timed out"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.RequestException as exc:
        return Response({"error": "Network error", "details": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as exc:
        return Response({"error": "Unexpected failure", "details": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
