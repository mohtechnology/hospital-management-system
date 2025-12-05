from django.contrib import admin
from .models import AvailabilitySlot, Booking

# Register your models here.
admin.site.register(AvailabilitySlot)
admin.site.register(Booking)