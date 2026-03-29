from rest_framework import serializers
from .models import Category, Tag, Service, Portfolio, Blog, Testimonial


# ---------------------------------------------------------------------------
# Primitives (used as inline embeds)
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description')


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

class PortfolioListSerializer(serializers.ModelSerializer):
    """Lightweight list: no description blob, just identity + thumbnails + category + tags."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ('id', 'name', 'slug', 'thumbnail', 'link',
                  'category', 'category_name', 'tags', 'created_at')


class PortfolioDetailSerializer(serializers.ModelSerializer):
    """Full portfolio including description, all services, and write support."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ('id', 'name', 'slug', 'description', 'thumbnail', 'link',
                  'category', 'category_name', 'tags', 'services',
                  'created_at', 'updated_at')
        extra_kwargs = {
            'thumbnail': {'required': False},
            'category': {'required': True},
        }

    def create(self, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().update(instance, validated_data)


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

class BlogListSerializer(serializers.ModelSerializer):
    """List view: no full content blob."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Write uses PK; read shows denormalised name only
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)

    class Meta:
        model = Blog
        fields = ('id', 'title', 'slug', 'short_description', 'thumbnail',
                  'category', 'category_name', 'created_at')


class BlogDetailSerializer(serializers.ModelSerializer):
    """Full blog post with content, category object, and tags."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = ('id', 'title', 'slug', 'short_description', 'thumbnail',
                  'content', 'category', 'tags', 'created_at', 'updated_at')
        extra_kwargs = {'thumbnail': {'required': False}}

    def create(self, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().update(instance, validated_data)


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ('id', 'name', 'position', 'title', 'description',
                  'avatar', 'rating', 'created_at')
        read_only_fields = ('created_at',)
