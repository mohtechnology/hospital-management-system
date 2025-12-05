import datetime
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def to_gcal_format(iso_dt):
    dt = datetime.datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
    return dt.strftime("%Y%m%dT%H%M%SZ")


def gcal_link_for_patient(doctor_name, start_iso, end_iso):
    start = to_gcal_format(start_iso)
    end = to_gcal_format(end_iso)

    return (
        "https://calendar.google.com/calendar/render"
        f"?action=TEMPLATE"
        f"&text=Appointment+With+Dr+{doctor_name}"
        f"&dates={start}/{end}"
        f"&details=Your+appointment+with+Dr+{doctor_name}"
    )

def gcal_link_for_doctor(patient_name, start_iso, end_iso):
    start = to_gcal_format(start_iso)
    end = to_gcal_format(end_iso)

    return (
        "https://calendar.google.com/calendar/render"
        f"?action=TEMPLATE"
        f"&text=Appointment+With+Patient+{patient_name}"
        f"&dates={start}/{end}"
        f"&details=Appointment+Booked+by+Patient+{patient_name}"
    )


def build_patient_email_html(doctor_name, slot):
    start_iso = slot.start.isoformat()
    end_iso = slot.end.isoformat()

    gcal_link = gcal_link_for_patient(doctor_name, start_iso, end_iso)

    return f"""
        <h2>Your Appointment is Confirmed ✔</h2>

        <p><b>Doctor:</b> Dr. {doctor_name}</p>
        <p><b>Time:</b> {slot.start.strftime('%H:%M %d-%m-%Y')} - {slot.end.strftime('%H:%M %d-%m-%Y')}</p>

        <a href="{gcal_link}"
           style="background:#1a73e8;color:white;padding:12px 20px;
           text-decoration:none;border-radius:8px;font-size:16px;">
           ➕ Add to Google Calendar
        </a>

        <br><br>
        <p>Thank you for using HMS!</p>
    """


def build_doctor_email_html(patient_user, slot):
    start_iso = slot.start.isoformat()
    end_iso = slot.end.isoformat()

    gcal_link = gcal_link_for_doctor(patient_user.username, start_iso, end_iso)

    return f"""
        <h2>New Appointment Booked ✔</h2>

        <p><b>Patient Name:</b> {patient_user.username}</p>
        <p><b>Patient Email:</b> {patient_user.email}</p>

        <p><b>Appointment Time:</b>
        {slot.start.strftime('%H:%M %d-%m-%Y')} - {slot.end.strftime('%H:%M %d-%m-%Y')}</p>

        <a href="{gcal_link}"
           style="background:#1a73e8;color:white;padding:12px 20px;
           text-decoration:none;border-radius:8px;font-size:16px;">
           ➕ Add to Google Calendar
        </a>

        <br><br>
        <p>You have a new appointment scheduled.</p>
    """


def send_appointment_emails(doctor_user, patient_user, slot):
    try:
        msg = EmailMultiAlternatives(
            "Appointment Confirmation",
            "",
            settings.EMAIL_HOST_USER,
            [patient_user.email],
        )
        msg.attach_alternative(
            build_patient_email_html(doctor_user.username, slot),
            "text/html",
        )
        msg.send()
        print(f"Email sent to patient: {patient_user.email}")
    except Exception as e:
        print("EMAIL ERROR (patient):", e)

    try:
        msg = EmailMultiAlternatives(
            "New Appointment Booked",
            "",
            settings.EMAIL_HOST_USER,
            [doctor_user.email],
        )
        msg.attach_alternative(
            build_doctor_email_html(patient_user, slot),
            "text/html",
        )
        msg.send()
        print(f"Email sent to doctor: {doctor_user.email}")
    except Exception as e:
        print("EMAIL ERROR (doctor):", e)


def send_cancellation_emails(doctor_user, patient_user, slot):

    subject = "Appointment Cancelled"

    start_time = f"{slot.start.strftime('%Y-%m-%d %H:%M')}"


    patient_html = f"""
        <h2>Your Appointment Has Been Cancelled ❌</h2>

        <p><b>Doctor:</b> Dr. {doctor_user.username}</p>
        <p><b>Original Time:</b> {start_time}</p>

        <p>Your appointment has been successfully cancelled.</p>
    """

    try:
        msg = EmailMultiAlternatives(
            subject,
            "",
            settings.EMAIL_HOST_USER,
            [patient_user.email],
        )
        msg.attach_alternative(patient_html, "text/html")
        msg.send()
    except Exception as e:
        print("CANCEL EMAIL ERROR (patient):", e)

    doctor_html = f"""
        <h2>Appointment Cancelled ❌</h2>

        <p><b>Patient:</b> {patient_user.username}</p>
        <p><b>Original Time:</b> {start_time}</p>

        <p>The patient has cancelled the appointment.</p>
    """

    try:
        msg = EmailMultiAlternatives(
            subject,
            "",
            settings.EMAIL_HOST_USER,
            [doctor_user.email],
        )
        msg.attach_alternative(doctor_html, "text/html")
        msg.send()
    except Exception as e:
        print("CANCEL EMAIL ERROR (doctor):", e)
