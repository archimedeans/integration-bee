from upload_validator import FileTypeValidator

from django import forms
# from django.utils.html import escape
# from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy as _


class SubmitForProblemForm(forms.Form):
    solution = forms.FileField(
        required=True,
        max_length=40,
        help_text='Upload your solution (PDF only; size up to 5 MB; '
                  + 'file name up to 40 characters long)',
        # allow_empty_file=False,
        widget=forms.FileInput(
            attrs={'id': 'solutionInput',
                   'class': 'form-control',
                   'accept': '.pdf,application/pdf'}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.has_error('solution'):
            self.fields['solution'].widget.attrs.update({
                'class': 'form-control is-invalid',
                'aria-describedby': 'solutionValidationFeedback'
            })

    def clean_solution(self):
        file = self.cleaned_data['solution']
        # if not file.name.endswith('.pdf'):
        #     raise ValidationError(
        #         _('The extension of the file is not \'.pdf\'.'),
        #         code='invalid'
        #     )

        # Use django-upload-validator for file validation
        # It checks the extension and MIME type of an uploaded file
        # inferred from the file name and the binary signature / magic number
        # using python-magic, which in turn uses the libmagic C library
        validator = FileTypeValidator(
            allowed_types=['application/pdf'],
            allowed_extensions=['.pdf']
        )
        # with file.open() as file_resource:
        file_resource = file.open()
        validator(file_resource)
        return file


class ContactForm(forms.Form):
    email = forms.EmailField(
        required=True,
        help_text='The email address you would like us to send our response to',
    )
    subject = forms.ChoiceField(
        required=True,
        choices=[
            ('paper', 'Contest paper'),
            ('website', 'Website'),
            ('other', 'Other')
        ],
    )
    message = forms.CharField(
        required=True,
        min_length=5,
        strip=True,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        input_classes = {
            'email': 'form-control',
            'subject': 'form-select',
            'message': 'form-control'
        }

        for field_name in ('email', 'subject', 'message'):
            if not self.has_error(field_name):
                self.fields[field_name].widget.attrs.update({
                    'class': input_classes[field_name],
                })
            else:
                self.fields[field_name].widget.attrs.update({
                    'class': input_classes[field_name] + ' is-invalid',
                    'aria-describedby': field_name + 'ValidationFeedback'
                })

    # def clean_message(self):
    #     return escape(self.cleaned_data['message'])
