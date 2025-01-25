from ...models import Settings


class TokenSettings:
    def __init__(self):
        self.settings = Settings.objects.all().first()
        
    