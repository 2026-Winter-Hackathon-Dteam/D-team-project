from django import forms
from .models import Spaces

class SpaceEditForm(forms.ModelForm):
    class Meta:
        model = Spaces
        fields = ['name']  # 編集可能なフィールドを指定
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }