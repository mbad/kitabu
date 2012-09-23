from django import forms

from kitabu.forms.validators import BaseValidator


class KitabuForm(forms.Form):
    error_css_class = 'error'

    extra_field_validators = {}
    extra_form_validators = []

    def __init__(self, *args, **kwargs):
        super(KitabuForm, self).__init__(*args, **kwargs)

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
        return super(KitabuForm, self).clean()
