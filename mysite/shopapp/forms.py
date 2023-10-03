from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'price', 'description', 'discount', 'preview'

    # adding a new field:
    images = forms.ImageField(
        # to have an option of adding many images at the time, we have to tag this widget:
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
