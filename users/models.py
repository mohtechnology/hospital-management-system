from django.db import models
from django.contrib.auth.models import User
import json

ROLE_CHOICES = (("doctor", "Doctor"), ("patient", "Patient"))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="patient")
    specialization = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    google_credentials = models.TextField(blank=True, null=True)  # JSON string

    def set_google_credentials(self, creds: dict):
        self.google_credentials = json.dumps(creds)

    def get_google_credentials(self):
        if not self.google_credentials:
            return None
        return json.loads(self.google_credentials)

    def __str__(self):
        return f"{self.user.username} Profile ({self.role})"
