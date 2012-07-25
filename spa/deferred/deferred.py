from django.db import models

class DeferredField(object):
    def __init__(self, cls = None):
        self.cls = cls

    def construct(self, cls = None):
        '''When fixing defered field we give it referenced model
        and may update it's properties'''

        if cls is not None:
            return cls
        elif self.cls is None:
            raise TypeError("Implementation of every field is required")
        else:
            return self.cls


class DeferredForeignKey(DeferredField):
    def __init__(self):
        self.cls = None


class DeferredModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def settle(cls, **kwargs):
        new_fields = {}
        # for every class in hierarchy
        # ordered by python's method resoultion order
        for c in reversed(cls.__mro__):
            # inspect all fields of that class
            for field_name, field in c.__dict__.iteritems():
                # to find DeferedField instances
                if isinstance(field, DeferredField):
                    if field_name in kwargs:
                        # and settle them
                        new_fields[field_name] = field.construct( kwargs.pop(field_name) )
                    else: # if field_name in kwargs:
                        # or raise error if implementation not given
                        # TODO  fix error class
                        new_fields[field_name] = field.construct()
        if len(kwargs) > 0:
            # if to many arguments given then probably some error
            raise TypeError("Superficient keyword arguments to settle model")
        # when all field are extracted set them for the class
        for k, v in new_fields.iteritems():
            #setattr(cls, k, v)
            cls.add_to_class(k, v)
        return cls