from django.shortcuts import render, redirect
from django.views.generic import TemplateView

class TopView(TemplateView):
    template_name = "accounts/top.html"

def members(request):
    return render(request, "accounts/members.html")

def profile(request):
    return render(request, "accounts/profile.html")

def edit_member(request):
    return render(request, "accounts/edit_member.html")

def change_password(request):
    return render(request, "accounts/change_password.html")