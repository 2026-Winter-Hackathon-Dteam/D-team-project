from django import forms

class QuestionForm(forms.Form):
    name = forms.CharField()