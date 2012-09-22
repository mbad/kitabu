from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from kitabu.forms.validators import BaseValidator


class KitabuBaseForm(forms.Form):
    error_css_class = 'error'

    extra_field_validators = {}
    extra_form_validators = []

    def __init__(self, *args, **kwargs):
        super(KitabuBaseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True

        for validator_name, validator in self.extra_field_validators.iteritems():
            if validator_name in self.fields:
                if  isinstance(validator, BaseValidator):
                    self.base_fields[validator_name].append(validator)
                elif isinstance(validator, list):
                    self.base_fields[validator_name].extend(validator)
                else:
                    assert False, "Only Validators derived from BaseValidator or lists of them are allowed"

    def clean(self):
        for validator in self.extra_form_validators:
            validator(self)
        return super(KitabuBaseForm, self).clean()


class KitabuSearchForm(KitabuBaseForm):
    def __init__(self, *args, **kwargs):
        super(KitabuSearchForm, self).__init__(*args, **kwargs)
        self.helper.form_method = 'get'
        self.helper.add_input(Submit('submit', 'Search'))


class KitabuPostForm(KitabuBaseForm):
    '''
    Base class for post forms.
    Customisation of submit button text can be done via
    submit_button_text field of either class or instance
    '''

    submit_button_text = "Submit"

    def __init__(self, *args, **kwargs):
        super(KitabuPostForm, self).__init__(*args, **kwargs)
        self.helper.form_method = 'post'  # this is default, but for explicity it's here
        submit_button_text = self.submit_button_text
        self.helper.add_input(Submit('submit', submit_button_text))
