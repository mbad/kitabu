from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class KitabuBaseForm(forms.Form):
    error_css_class = 'error'

    validators = {}

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.html5_required = True
        super(KitabuBaseForm, self).__init__(*args, **kwargs)


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
