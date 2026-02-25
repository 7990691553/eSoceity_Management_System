from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import UserSignupForm, UserLoginForm

# Create your views here.
def UserSignupView(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
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