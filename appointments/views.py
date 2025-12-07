from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware, is_naive, now
from django.db import transaction
from datetime import datetime, timedelta, date
from django.contrib import messages
from django.contrib.auth.models import User

from .models import AvailabilitySlot, Booking
from .utils import send_appointment_emails, send_cancellation_emails


def generate_time_choices():
    times = []
    hour = 0
    minute = 0

    while hour < 24:
        times.append({
            "value": f"{hour:02d}:{minute:02d}",
            "label": f"{hour:02d}:{minute:02d}",
        })
        minute += 30
        if minute == 60:
            minute = 0
            hour += 1

    return times


@login_required
def doctor_dashboard(request):
    if request.user.profile.role != "doctor":
        messages.error(request, "Unauthorized access!")
        return redirect("home")

    time_choices = generate_time_choices()

    if request.method == "POST":
        date_str = request.POST.get("date")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")

        if not date_str or not start_time_str or not end_time_str:
            messages.error(request, "All fields are required.")
            return redirect("appointments:doctor_dashboard")

        try:
            start_naive = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_naive = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect("appointments:doctor_dashboard")

        start_dt = make_aware(start_naive)
        end_dt = make_aware(end_naive)

        if start_dt >= end_dt:
            messages.error(request, "End time must be later than start time.")
            return redirect("appointments:doctor_dashboard")

        duration = 30
        current = start_dt

        slot_count = 0

        while current + timedelta(minutes=duration) <= end_dt:
            slot_end = current + timedelta(minutes=duration)

            if current > now():
                AvailabilitySlot.objects.get_or_create(
                    doctor=request.user,
                    start=current,
                    end=slot_end,
                )
                slot_count += 1

            current = slot_end

        messages.success(request, f"{slot_count} slots created successfully!")
        return redirect("appointments:doctor_dashboard")

    today = date.today()
    available_dates = [today + timedelta(days=i) for i in range(30)]

    all_slots = AvailabilitySlot.objects.filter(
        doctor=request.user
    ).order_by("start")

    selected_date_str = request.GET.get("filter_date")
    selected_date = None

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date selected.")
            selected_date = None

    slots = all_slots.filter(start__date=selected_date) if selected_date else all_slots

    return render(request, "appointments/doctor_dashboard.html", {
        "slots": slots,
        "time_choices": time_choices,
        "available_dates": available_dates,
        "selected_date": selected_date_str,
    })


@login_required
def doctors_list(request):

    doctors = User.objects.filter(profile__role="doctor")

    selected_doctor_id = request.GET.get("doctor_id")
    selected_date_str = request.GET.get("date")
    selected_date_obj = None
    doctor = None
    slots = []

    today = date.today()
    available_dates = [today + timedelta(days=i) for i in range(30)]

    if selected_doctor_id:
        try:
            doctor = User.objects.get(pk=selected_doctor_id)
        except User.DoesNotExist:
            messages.error(request, "Doctor not found.")
            return redirect("appointments:doctors_list")

        doctor_slots = AvailabilitySlot.objects.filter(
            doctor=doctor,
            booked=False,
            start__gt=now(),
        ).order_by("start")

        if selected_date_str:
            try:
                selected_date_obj = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date selected.")
                selected_date_obj = None

        if selected_date_obj:
            slots = doctor_slots.filter(start__date=selected_date_obj)

    return render(request, "appointments/doctors_list.html", {
        "doctors": doctors,
        "selected_doctor": doctor,
        "selected_date": selected_date_str,
        "available_dates": available_dates,
        "slots": slots,
    })


@login_required
def book_slot(request, slot_id):

    if request.user.profile.role != "patient":
        messages.error(request, "Only patients can book appointments.")
        return redirect("home")

    slot = get_object_or_404(AvailabilitySlot, pk=slot_id)

    try:
        with transaction.atomic():
            locked = AvailabilitySlot.objects.select_for_update().get(pk=slot_id)

            if locked.booked:
                messages.error(request, "This slot has already been booked.")
                return render(request, "appointments/booking_failed.html")

            locked.booked = True
            locked.save()

            Booking.objects.create(slot=locked, patient=request.user)

    except Exception as e:
        messages.error(request, "Something went wrong while booking the slot.")
        return render(request, "appointments/booking_failed.html")

    send_appointment_emails(doctor_user=locked.doctor, patient_user=request.user, slot=locked)

    messages.success(request, "Appointment booked successfully!")
    return redirect("appointments:my_bookings")


@login_required
def my_bookings(request):

    if request.user.profile.role == "doctor":
        bookings = Booking.objects.filter(slot__doctor=request.user).order_by("slot__start")
    else:
        bookings = Booking.objects.filter(patient=request.user).order_by("slot__start")

    return render(request, "appointments/my_bookings.html", {"bookings": bookings})


@login_required
def cancel_booking(request, booking_id):

    booking = get_object_or_404(Booking, pk=booking_id)

    if request.user != booking.patient:
        messages.error(request, "You cannot cancel this booking.")
        return redirect("appointments:my_bookings")

    slot = booking.slot

    slot.booked = False
    slot.save()

    send_cancellation_emails(
        doctor_user=slot.doctor,
        patient_user=request.user,
        slot=slot
    )

    booking.delete()

    messages.success(request, "Your appointment has been canceled.")
    return redirect("appointments:my_bookings")
