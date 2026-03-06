from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse

from .forms import UserSignupForm, UserLoginForm


def UserSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            # 1) Save user first (safe)
            user = form.save()

            # 2) Send confirmation email (non-blocking for signup)
            try:
                send_mail(
                    subject="eSociety Portal – Registration Confirmation",
                    message=(
                        "Dear User,\n\n"
                        "This is to inform you that your account has been successfully "
                        "registered in the eSociety Management System.\n\n"
                        "You may now log in using your registered credentials to access "
                        "society services, notices, and other relevant features.\n\n"
                        "If you did not initiate this registration, please contact the "
                        "system administrator immediately.\n\n"
                        "Regards,\n"
                        "eSociety Administration\n"
                        "Automated System Notification"
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception:
                # Email failure shouldn't stop signup
                messages.warning(request, "Account created, but email could not be sent right now.")

            messages.success(request, "Signup successful. Please login.")
            return redirect("core:login")  # ✅ use namespaced url

        messages.error(request, "Please correct the errors below.")
        return render(request, "core/signup.html", {"form": form})

    form = UserSignupForm()
    return render(request, "core/signup.html", {"form": form})


def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is inactive. Please contact admin.")
                    return render(request, "core/login.html", {"form": form})

                login(request, user)

                # Respect next=... if user tried to open a protected page
                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)

                # ✅ Always redirect to society dashboard redirect
                return redirect("society:dashboard_redirect")

            messages.error(request, "Invalid email or password.")
            return render(request, "core/login.html", {"form": form})

        messages.error(request, "Please correct the form errors.")
        return render(request, "core/login.html", {"form": form})

    form = UserLoginForm()
    return render(request, "core/login.html", {"form": form})

def userLogoutView(request):
    logout(request)
    return redirect("core:login")