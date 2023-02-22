from django import forms

class MatrixChoiceForm(forms.Form):
    width = forms.IntegerField(max_value=8, min_value=2, required=True, 
                               widget=forms.NumberInput, label="Width of Matrix", initial=3)
    height = forms.IntegerField(max_value=8, min_value=2, required=True, 
                               widget=forms.NumberInput, label="Height of Matrix", initial=3)
    
    