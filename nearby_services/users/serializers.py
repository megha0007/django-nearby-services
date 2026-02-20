__author__ = "Megha Shinde"
__date__ = "16-02-2026"
__lastupdatedby__ = "Megha Shinde"
__lastupdateddate__ = "16-02-2026"

from rest_framework import serializers
from .models import User, Service
from django.contrib.gis.geos import Point


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "is_active", "date_joined"]


class ServiceSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
# Use these for output (GET)
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'category', 'rating', 'metadata', 
            'lat', 'lng', 'latitude', 'longitude'
        ]

    # These methods extract the coordinates from the PointField
    def get_lat(self, obj):
        return obj.location.y if obj.location else None

    def get_lng(self, obj):
        return obj.location.x if obj.location else None

    def create(self, validated_data):
        lat = validated_data.pop('latitude')
        lng = validated_data.pop('longitude')

        validated_data['location'] = Point(lng, lat)

        return Service.objects.create(**validated_data)
