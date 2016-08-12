# forms.py
from django import forms
from django.forms import formset_factory
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from datetime import datetime as dt
from pi.models import *

###################################################
#
#	Contact forms
#
###################################################


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, help_text='100 characters max.')
    email = forms.EmailField(help_text='A valid email address, please.')
    subject = forms.ChoiceField(choices=(
        ('c', 'General customer service'),
        ('s', 'Suggestions'),
        ('p', 'Product support'),
    ))
    message = forms.CharField(widget=forms.Textarea)

###################################################
#
#	Attachment forms
#
###################################################


class AttachmentForm(ModelForm):

    class Meta:
        model = Attachment
        fields = ['description', 'file']
