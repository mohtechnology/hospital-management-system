from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def signup(request):
    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        role = request.POST.get("role")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return redirect("users:signup")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("users:signup")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect("users:signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("users:signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("users:signup")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
        except Exception as e:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("users:signup")

        try:
            user.refresh_from_db()
            user.profile.role = role
            user.profile.save()
        except Exception:
            messages.error(request, "Error creating profile. Contact support.")
            user.delete()  
            return redirect("users:signup")

        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("home")

    return render(request, "users/signup.html")


def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        # Empty fields
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("users:login")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect("users:login")

        login(request, user)
        messages.success(request, "Logged in successfully!")
        return redirect("home")

    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")

