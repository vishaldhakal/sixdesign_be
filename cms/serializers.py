from rest_framework import serializers
from .models import Category, Tag, Service, Portfolio, Blog

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class PortfolioListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'slug', 'thumbnail', 'category', 'category_name', 'tags']

class PortfolioDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = '__all__'
        extra_kwargs = {
            'thumbnail': {'required': False},
            'category': {'required': True}
        }

    def create(self, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().update(instance, validated_data)

class BlogListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'short_description', 'thumbnail', 'category', 'category_name']

class BlogDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Blog
        fields = '__all__'
        extra_kwargs = {
            'thumbnail': {'required': False}
        }

    def create(self, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'thumbnail' in validated_data and not validated_data['thumbnail']:
            validated_data.pop('thumbnail')
        return super().update(instance, validated_data) 