from django.db import models


class DeferredField(object):
    def __init__(self, cls=None, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def construct(self):
        if self.cls is None:
            raise TypeError("Implementation of every field is required")
        else:
            return self.cls(*self.args, **self.kwargs)


class DeferredForeignField(DeferredField):
    def __init__(self, cls, referenced_cls=None, *args, **kwargs):
        self.cls = cls
        self.referenced_cls = referenced_cls
        self.args = args
        self.kwargs = kwargs

    def construct(self, referenced_cls=None):
        if not referenced_cls:
            referenced_cls = self.referenced_cls
        if not referenced_cls:
            raise TypeError("Foreign model's class not given for ForeignField")
        return self.cls(referenced_cls, *self.args, **self.kwargs)


class DeferredModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def settle(cls, **kwargs):
        new_fields = {}
        # for every class in hierarchy
        # ordered by python's method resoultion order
        for c in cls.mro():
            # inspect all fields of that class
            for field_name, field in c.__dict__.iteritems():
                # to find DeferedField instances
                if (
                    isinstance(field, DeferredField)
                    # that are not settled yet
                    and not field_name in new_fields
                    # and are not members of current class
                    and not hasattr(cls, field_name)
                    ):
                    new_fields[field_name] = field.construct()
        # when all fields are extracted settle them for the class
        for k, v in new_fields.iteritems():
            #setattr(cls, k, v)
            cls.add_to_class(k, v)
        return cls
