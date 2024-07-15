from decimal import Decimal
import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver
from .models import Deposit, Earnings, Investment, UserProfile, Wallet, Withdrawal

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def create_user_wallet_and_earnings(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user_profile=instance)
        logger.info(f"Wallet created for user: {instance.user.username}")
        Earnings.objects.create(user_profile=instance, earnings=Decimal('0.00'))
        logger.info(f"Earnings created for user: {instance.user.username}")

@receiver(pre_delete, sender=Withdrawal)
def update_wallet_balance_on_withdrawal(sender, instance, **kwargs):
    wallet = instance.user_profile.wallet
    wallet.balance -= instance.amount
    wallet.save()
    logger.info(f"Wallet balance updated after withdrawal for user: {instance.user_profile.user.username}")

@receiver(post_save, sender=Deposit)
def update_wallet_balance(sender, instance, created, **kwargs):
    if not created and instance.status == 'approved':
        wallet = Wallet.objects.get(user_profile=instance.user_profile)
        wallet.balance += instance.amount
        wallet.save()
        
        # Create an active investment
        investment = Investment.objects.create(user_profile=instance.user_profile, amount=instance.amount)
        logger.info(f"Investment of {instance.amount} created for user: {instance.user_profile.user.username}")
