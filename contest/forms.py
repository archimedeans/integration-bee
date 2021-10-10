from django.contrib.auth import forms as auth_forms
from django import forms
from django.utils.translation import ugettext_lazy as _


class BootstrapAuthenticationForm(auth_forms.AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'username'}
    ))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'password'}
    ))


class BootstrapPasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        placeholders = {
            'old_password': 'old password',
            'new_password1': 'new password',
            'new_password2': 'confirm new password'
        }
        feedback_id_starts = {
            'old_password': 'oldPassword',
            'new_password1': 'newPassword1',
            'new_password2': 'newPassword2'
        }

        self.fields['new_password2'].label = _("Confirm new password")

        for field_name in ('old_password', 'new_password1', 'new_password2'):
            if not self.has_error(field_name):
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': placeholders[field_name]
                })
            else:
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control is-invalid',
                    'placeholder': placeholders[field_name],
                    'aria-describedby': feedback_id_starts[field_name] + 'ValidationFeedback'
                })
