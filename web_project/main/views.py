from django.shortcuts import render, redirect
from .forms import PictureForm


# Create your views here.


def home(request):
    form = PictureForm()
    context = {
        'form': form
    }
    return render(request, 'main/index.html', context)


def analyze_full(request):
    if request.method == "POST":
        form = PictureForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(form.instance.processed_image.url)
