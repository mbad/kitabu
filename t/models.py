from django.db import models
from kitabu.models.constraints import Constraint


class Constraint(Constraint):

    # zero or more subjects can use this constraing
    lanes = models.ManyToManyField('lanes.Lane', related_name='instance_constraints', blank=True)
