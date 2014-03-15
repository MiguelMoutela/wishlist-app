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

ESTIMATION_ATTRS = {
    'class': 'form-control',
    'placeholder': _('Estimated price')
}

CONTRIBUTION_ATTRS = {
    'class': 'form-control',
    'placeholder': _('My contribution')
}


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


class ContributionForm(forms.Form):

    estimation = forms.DecimalField(
        min_value=0, max_digits=11, decimal_places=2,
        widget=forms.NumberInput(attrs=ESTIMATION_ATTRS))
    contribution = forms.DecimalField(
        min_value=0, max_digits=11, decimal_places=2,
        widget=forms.NumberInput(attrs=CONTRIBUTION_ATTRS))
