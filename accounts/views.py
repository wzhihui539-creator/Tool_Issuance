from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .decorators import role_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        return render(request, "accounts/login.html", {"error": "用户名或密码错误"})
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def home(request):
    roles = list(request.user.groups.values_list("name", flat=True))
    return HttpResponse(f"Hello {request.user.username}. roles={roles}")

@login_required
@role_required("worker")
def worker_page(request):
    return HttpResponse("worker only ✅")

@login_required
@role_required("keeper")
def keeper_page(request):
    return HttpResponse("keeper only ✅")

@login_required
@role_required("supervisor")
def supervisor_page(request):
    return HttpResponse("supervisor only ✅")
