__author__ = "Megha Shinde"
__date__ = "16-02-2026"
__lastupdatedby__ = "Megha Shinde"
__lastupdateddate__ = "18-02-2026"

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('user', 'User'),
)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    location = models.PointField(srid=4326)  # GIS field ✅
    rating = models.FloatField(default=0)
    metadata = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("create_user", "Create User"),
        ("update_role", "Update Role"),
        ("toggle_status", "Enable/Disable User"),
    ]

    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="performed_actions")
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="targeted_actions", null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

