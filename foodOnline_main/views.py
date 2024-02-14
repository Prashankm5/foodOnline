from django.shortcuts import render
from django.http import HttpResponse


# Home
def home(request):
    return render(request, 'home.html')