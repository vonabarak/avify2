# -*- coding: utf-8 -*-

from django import forms

class AddProxyForm(forms.Form):
    name = forms.CharField(label='host name', required=True)
    port = forms.IntegerField(label='port', required=True, initial=80)
    login = forms.CharField(label='login',required=False)
    passwd = forms.CharField(label='password', required=False)
    prio = forms.IntegerField(label='prio', required=True, initial=10)


class AddSearchCathegoryForm(forms.Form):
    name = forms.CharField(label='cathegory name', required=True)
    url = forms.URLField(label='cathegory url', required=True)


class AddSearchForm(forms.Form):
    # cathegory = forms.ChoiceField(choices=[
    #     (c.id, u'{}'.format(c.name)) for c in SearchCathegory.objects.all()
    # ], required=True)
    # user = forms.ChoiceField(choices=[
    #     (c.id, u'{}'.format(c.name)) for c in TgUser.objects.all()
    #     ], required=True)
    keywords = forms.CharField(label='search keywords', required=True)
    price_min = forms.IntegerField(label='price min', required=True, initial=0)
    price_max = forms.IntegerField(label='price max', required=True, initial=10**6)

    def __init__(self, cathegory_choices, user_choices, *args, **kwargs):
        super(AddSearchForm, self).__init__(*args, **kwargs)
        self.fields['cathegory'] = forms.ChoiceField(choices=cathegory_choices, required=True)
        self.fields['user'] = forms.ChoiceField(choices=user_choices, required=True)

