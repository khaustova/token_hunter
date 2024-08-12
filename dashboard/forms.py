from django import forms
from .widgets import MEditorWidget

   
class MEditorFormField(forms.fields.CharField):
    def __init__(self, config_name='default', *args, **kwargs):
        kwargs.update({
            'widget': MEditorWidget()
        })
        super(MEditorFormField, self).__init__(*args, **kwargs)   