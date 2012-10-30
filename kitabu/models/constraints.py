from importlib import import_module

from django.db import models

from kitabu.exceptions import ValidationError


class Constraint(models.Model):

    class Meta:
        abstract = True

    # zero or more models can use this constraint:
    subject_type = models.ManyToManyField('contenttypes.ContentType', related_name='model_constraints', blank=True)
    # zero or more subjects can use this constraing
    #subjects = models.ManyToManyField('Subject', related_name='instance_constraints')

    # dotted absolute path to class implementing given constraint:
    constraint_class = models.CharField(max_length=200)
    # if constraint class is Model we are intereseted in certain object:
    constraint_instance_id = models.PositiveIntegerField(null=True, blank=True)

    def get_validator(self):
        module_name, class_name = self.constraint_class.rsplit('.', 1)
        validator_class = getattr(import_module(module_name), class_name)
        args = [self.constraint_instance_id] if self.constraint_instance_id else []
        return validator_class(*args)


class ValidateNever(object):
    def validate(self, reservation):
        raise ValidationError('Reservation of this subject is not possible')
