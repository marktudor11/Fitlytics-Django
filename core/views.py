from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home.html")

def nutrition(request):
    return render(request, "nutrition.html")

def training(request):
    return render(request, "training.html")

def metrics(request):
    return render(request, "metrics.html")