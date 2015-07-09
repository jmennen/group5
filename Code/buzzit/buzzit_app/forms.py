from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

#form to display user registration 

class RegistrationForm(forms.Form):
    # form fields for user registration, use widget class which give us the opportunity to customize form field with different attributes under circumstances
    
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Username"), error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Vorname"))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Nachname"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)"))

    def clean_username(self):
        # cleaning method that operates on the form field username, default case username is not taken
        # check if the given username exists already, in this case throw a message, when not, store the username
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("Der Benutzername existiert bereits."))

    def clean(self):
        # cleaning method that operates on the form fields password 
        # check if the passwords are valid, and when the given passwords don't match, throw a error
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("Die Passworte stimmen leider nicht überein."))
        return self.cleaned_data
