from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone

from accounts.models import *
from backend.models import *


class LocationPingSerializer(serializers.ModelSerializer):

    created_at = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = LocationPing
        fields = [
            'location_ping_id', 
            'lat',
            'lng',
            'geocoordinate',
            'altitude',
            'accuracy',
            'heading',
            'speed',
            'timestamp',
            'user',
            'created_at',
            'status',
        ]
    
    def get_timestamp(self, obj):
        date = obj.timestamp
        date_object = None
        if date:
            date_object = {
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'hour': date.hour,
                'minute': date.minute,
                'second': date.second,
                'timezone': timezone.get_current_timezone_name()
            }
        return date_object
    
    def get_created_at(self, obj):
        date = obj.created_at
        date_object = None
        if date:
            date_object = {
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'hour': date.hour,
                'minute': date.minute,
                'second': date.second,
                'timezone': timezone.get_current_timezone_name()
            }
        return date_object
    
    def get_user(self, obj):
        if obj.user:
            return obj.user.email
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove fields with null values or empty strings
        return {key: value for key, value in data.items() if value is not None and value != ""}