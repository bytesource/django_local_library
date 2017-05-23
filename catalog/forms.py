
import datetime  # For checking the date range of the renewal date.
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django import forms

# NOTE: Form class is ideal if you need to include data from several
# different models into the form.


class RenewBookForm(forms.Form):
    # Form has the same field types as Model, and then some:
    # https://docs.djangoproject.com/en/1.10/ref/forms/fields/#built-in-field-classes
    # NOTE: All Field subclasses have required=True by default.
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks in the future (default is 3).",
        widget=forms.DateInput,  # https://docs.djangoproject.com/en/1.11/ref/forms/widgets/
    )

    # NOTE: Override the method clean_<fieldname>() for the field you want to
    # check.
    def clean_renewal_date(self):
        # self.cleaned_data[...]:
        # -- Sanitized of potentially unsafe input using the default validators, and
        # -- converted into the correct standard type for the data
        #    (in this case a Python datetime.datetime object).
        data = self.cleaned_data['renewal_date']

        # Check date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_("Invalid date - Renewal in the past"))

        # Check date is not out of range.
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _("Invalid date - Renewal more than 4 weeks in the future"))

        # Always return data.
        return data

        # NOTE: How to validate interdependent fields: Override the clean() method of the Form class:
        #       https://docs.djangoproject.com/en/1.10/ref/forms/validation/#validating-fields-with-clean
        #       1) By the time the form’s clean() method is called,
        #          all the individual field clean methods will have been run.
        #          => The fields you are wanting to validate might not have survived the initial individual field checks.


# NOTE: The following form is based on ModelForm, which is ideal for forms with data from a SINGLE model.
#       (Pulls a lot of data from the respective model via a Meta class,
#        so much less typing compared to Form class.)
'''
from django.forms import ModelForm
from .models import BookInstance

class RenewBookModelForm(ModelForm):
    # NOTE:
    # clean_<due_back> instead of clean_<renewal_date> as above, because 'due_back' is the 
    # name of the respective BookInstance model field.
    # NOTE: The rest of the validation logic is the same as above.
    def clean_due_back(self):
       data = self.cleaned_data['due_back'] # Again, 'due_back' instead of 'renewal_date'
       
       #Check date is not in past.
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       #Check date is in range librarian allowed to change (+4 weeks)
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
       return data

    # NOTE: Don't forget to add Meta class. 
    class Meta:
        # Mandatory
        model = BookInstance
        fields = ['due_back',]
        # fields = __all__ # Get all fields.
        # fields = exclude(<fieldname>, <fieldname>) # Get all fields, except for these.

        # Optional: Labels, widgets, help text, error messages.
        # By default the values of these will be retrieved from the BookInstance Class.
        labels     = { 'due_back': _('Renewal date'), }
        help_texts = { 'due_back': _('Enter a date between now and 4 weeks (default 3).'), }
'''
