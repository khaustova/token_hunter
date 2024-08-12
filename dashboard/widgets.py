from django import forms


class MEditorWidget(forms.Textarea):
    template_name = 'dashboard/bot_message_editor.html'

    def _get_media(self):
        return forms.Media(
            css={
                "all": ("dashboard/css/bot.css",)
            },
            js=(
                "dashboard/js/bot_message_editor.js",
            ))
    media = property(_get_media)