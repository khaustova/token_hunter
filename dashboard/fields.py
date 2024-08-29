from django.db import models
from .forms import MEditorFormField


class MEditorField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': MEditorFormField,
        }
        defaults.update(kwargs)
        return super(MEditorField, self).formfield(**defaults)