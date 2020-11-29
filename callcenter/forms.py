from django.forms import ModelForm
from .models import Main


class MainForm(ModelForm):
    model = Main
    fields = ['date', 'project', 'price', 'number',
               'used', 'source', 'formation', 'responsible',
               'link', 'status', 'comments']