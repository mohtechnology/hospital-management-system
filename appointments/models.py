from django.db import models
from django.contrib.auth.models import User

class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doctor_slots")
    start = models.DateTimeField()
    end = models.DateTimeField()
    booked = models.BooleanField(default=False)

    class Meta:
        ordering = ["start"]
        unique_together = ("doctor", "start", "end")

    def __str__(self):
        return f"{self.doctor.username} — {self.start} to {self.end} ({'Booked' if self.booked else 'Free'})"


class Booking(models.Model):
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_bookings")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.username} → {self.slot}"
