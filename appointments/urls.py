from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("doctor-dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctors/", views.doctors_list, name="doctors_list"),
    path("book/<int:slot_id>/", views.book_slot, name="book_slot"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
]
