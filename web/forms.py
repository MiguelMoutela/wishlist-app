from django.utils.translation import ugettext_lazy as _
from django import forms
from models import Item

NAME_ATTRS = {
    'class': 'form-control',
    'placeholder': _('Name')
}

DESCRIPTION_ATTRS = {
    'class': 'form-control',
    'placeholder': _('Description')
}


class ItemForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs=NAME_ATTRS))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs=DESCRIPTION_ATTRS))

    class Meta:
        model = Item
        fields = ('name', 'description',)
