from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class SpaForm(forms.Form):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super(SpaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True


class SearchForm(SpaForm):
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper.form_method = 'get'
        self.helper.add_input(Submit('submit', 'Search'))


class PostForm(SpaForm):
    '''
    Base class for post forms.
    Customisation of submit button text can be done via
    submit_button_text field of either class or instance
    '''

    submit_button_text = "Submit"

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.helper.form_method = 'post'  # this is default, but for explicity it's here
        submit_button_text = self.submit_button_text
        self.helper.add_input(Submit('submit', submit_button_text))
