from django.shortcuts import render
from django.http import HttpResponse

def sample(request):
    return render(request, "teams/teams.html")
