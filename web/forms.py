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

MULTI_ITEM_LABEL = _('More people can buy this item')


class ItemForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs=NAME_ATTRS))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs=DESCRIPTION_ATTRS))
    multi_item = forms.BooleanField(
        required=False,
        label=MULTI_ITEM_LABEL)

    class Meta:
        model = Item
        fields = ('name', 'description', 'multi_item',)
