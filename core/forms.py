from django import forms
from django.forms import ModelForm
from .models import Glist, User


class GlistForm(ModelForm):
    login = forms.CharField(label='login', max_length=100)
    class Meta:
        model = Glist
        fields=['login']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].queryset = User.objects.none()
