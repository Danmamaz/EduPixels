from django.shortcuts import render 
from django.http import HttpResponse

# Create your views here.
def render_landing(request):
    return HttpResponse(request, "Welcome!")
