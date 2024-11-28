from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            
            if not user:
                # Try to authenticate with email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user:
                if not user.is_active:
                    raise serializers.ValidationError({
                        'detail': 'User account is disabled.'
                    })
                
                # Update attrs with the correct username
                attrs['username'] = user.username
                data = super().validate(attrs)
                data['user'] = UserSerializer(user).data
                return data
            else:
                raise serializers.ValidationError({
                    'detail': 'Unable to log in with provided credentials.'
                })
        else:
            raise serializers.ValidationError({
                'detail': 'Must include "username" and "password".'
            })

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        
        # Check if email already exists
        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        
        # Check if username already exists
        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
            
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user 