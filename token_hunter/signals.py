from django.db.models import signals
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import TopTrader


@receiver(pre_save, sender=TopTrader)
def update_all_transaction_counts(sender, instance, **kwargs):
    """Signal handler for updating transaction count for all top wallets with matching wallet_address.
    
    Note:
        - Temporarily disconnects the signal during update to prevent infinite recursion.
        - Updates all records with the given wallet_address, not just the current instance.

    Args:
        instance: TopTrader model instance being saved.
        sender: Model sending the signal (TopTrader).
        **kwargs: Additional signal arguments.
    """
    wallet_address = instance.wallet_address

    traders_with_same_wallet = TopTrader.objects.filter(wallet_address=wallet_address)

    transactions_count = len(traders_with_same_wallet)

    signals.pre_save.disconnect(update_all_transaction_counts, sender=sender)

    for trader in traders_with_same_wallet:
        trader.transaction_count = transactions_count
        trader.save()

    signals.pre_save.connect(update_all_transaction_counts, sender=sender)
