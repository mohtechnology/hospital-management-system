from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("users:signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("users:signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.refresh_from_db()

        user.profile.role = role
        user.profile.save()

        login(request, user)
        return redirect("home")

    return render(request, "users/signup.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect("users:login")

        login(request, user)
        return redirect("home")

    return render(request, "users/login.html")



def logout_view(request):
    logout(request)
    return redirect("home")

