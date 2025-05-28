from rest_framework import serializers
from token_hunter.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Transaction.
    
    Используется для преобразования объектов Transaction в JSON-формат и обратно при работе с API.
    """
    class Meta:
        """Мета-класс для настройки сериализатора.
        
        Attributes:
            model: Модель Django, которая сериализуется (Transaction)
            fields: Поля модели, которые включены в сериализацию (`PNL` и `mode`)
            depth: Глубина вложенности связанных объектов (1 уровень)
        """
        model = Transaction
        fields = ("PNL", "mode", "closing_date")
        depth = 1
