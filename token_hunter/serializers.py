from rest_framework import serializers
from token_hunter.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for the Transaction model.
    
    Handles conversion between Transaction objects and JSON format for API operations.
    """
    class Meta:
        """Meta class for serializer configuration.
        
        Attributes:
            model: Django model being serialized (Transaction).
            fields: Model fields included in serialization (PNL, mode, closing_date).
            depth: Nesting depth for related objects (1 level).
        """
        model = Transaction
        fields = ("PNL", "mode", "closing_date")
        depth = 1
