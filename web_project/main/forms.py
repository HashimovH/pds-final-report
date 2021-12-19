from django import forms

# import GeeksModel from models.py
from .models import Picture

# create a ModelForm


class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['picture', ]
        widgets = {
            'picture': forms.FileInput(attrs={'class': 'form-control form-control-lg', 'accept': 'image/*', })
        }
