from django import forms

class MatrixChoiceForm(forms.BaseForm):
    length = forms.CharField(max_length=2, empty_value="3", )
    width = forms.CharField(max_length=2, empty_value="3", )
    