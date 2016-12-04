# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from avify.resapp_constants import cathegories, regions
from avify.models import User


class AddSearchForm(forms.Form):
    cathegory = forms.ChoiceField(choices=[
         (c, u'{}'.format(n)) for c, n in cathegories.items()
     ], required=True)
    region = forms.ChoiceField(choices=[
         (c, u'{}'.format(n)) for c, n in regions.items()
     ], required=True, initial=637640)
    keywords = forms.CharField(required=True)
    price_min = forms.IntegerField(required=True, initial=0)
    price_max = forms.IntegerField(required=True, initial=10**6)
    search_by_description = forms.BooleanField(required=False, initial=False)

    def __init__(self, user_choices, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        if user_choices:
            self.fields['user'] = forms.ChoiceField(choices=user_choices, required=True)


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_staff', 'is_active']

class BroadcastMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)


class LoginForm(forms.Form):
    auth_token = forms.CharField(label=_('Authentication token'), required=True)