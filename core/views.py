from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home.html")

def nutrition(request):
    return render(request, "nutrition.html")

def training(request):
    # training template lives under the training app at training/templates/training/training.html
    return render(request, "training/training.html")

def metrics(request):
    return render(request, "metrics.html")