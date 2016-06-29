from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from models import Item

NAME_ATTRS = {
    'class': 'form-control',
    'placeholder': _('Item Name')
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


class WishlistAuthenticationForm(AuthenticationForm):

    def clean(self):
        """
        This clean method is copied verbatim from
        django.contrib.auth.forms.

        The only difference is that the usercame will be forced to
        lowercase before checking anything.
        """
        username = self.cleaned_data.get('username').lower()
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data
