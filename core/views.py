from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib import messages

from .forms import UserSignupForm, UserLoginForm

# Create your views here.
def UserSignupView(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
        #email send
        email = form.cleaned_data['email']
        send_mail(subject="eSociety Portal – Registration Confirmation",message="Dear User,\n\n"
                 "This is to inform you that your account has been successfully "
                 "registered in the eSociety Management System.\n\n"
                 "You may now log in using your registered credentials to access "
                 "society services, notices, and other relevant features.\n\n"
                 "If you did not initiate this registration, please contact the "
                 "system administrator immediately.\n\n"
                 "Regards,\n"
                 "eSociety Administration\n"
                 "Automated System Notification",from_email=settings.EMAIL_HOST_USER,recipient_list=[email])
        form.save()
        return redirect('login') #error
      else:
        return render(request,'core/signup.html',{'form':form})  
    else:
        form = UserSignupForm()
        return render(request,'core/signup.html',{'form':form})

def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")  # temporary redirect
            else:
                messages.error(request, "Invalid email or password.")

        return render(request, "core/login.html", {"form": form})

    form = UserLoginForm()
    return render(request, "core/login.html", {"form": form})