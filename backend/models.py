from django.db import models
from django.db.models import JSONField
import uuid

from django.conf import settings
from files.models import *
from accounts.models import *
from files.storage_config import *
from core.utils import *

import datetime

from rest_framework_api_key.models import AbstractAPIKey


# ====================================================================================================
# Models
# ====================================================================================================

class LocationPing(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=generate_model_id, editable=False)
    location_ping_id = models.CharField(editable=False, max_length=32, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    lat = models.FloatField(default=True)
    lng = models.FloatField(default=True)
    geocoordinate = models.CharField(max_length=128, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    accuracy = models.FloatField(default=True)
    altitude = models.FloatField(default=True)
    speed = models.FloatField(default=True)
    heading = models.FloatField(default=True)
    data = models.JSONField(null=True) # Include in all models for storing unstructured data if needed
    config = models.JSONField(null=True) # Include in all models for storing record config data if needed
    created_at = models.DateTimeField(auto_now_add=True) # Include in all models for when the record was created
    status = models.CharField(max_length=10, default="active") # Include in all models for archiving records

    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['location_ping_id'], name='location_ping_index'),
        ]


# ====================================================================================================
# UserLog
# ====================================================================================================

class UserLog(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=generate_model_id, editable=False)
    user_log_id = models.CharField(editable=False, max_length=32, null=True)
    valid = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    view_name = models.CharField(editable=False, max_length=128, null=True)
    http_request_type = models.CharField(editable=False, max_length=16, null=True)
    ip_address = models.CharField(editable=False, max_length=64, null=True)
    path = models.CharField(editable=False, max_length=1000, null=True)
    full_path = models.CharField(editable=False, max_length=1000, null=True)
    # Add specific objects here
    data = models.JSONField(null=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['user_log_id'], name='user_log_index'),
        ]
