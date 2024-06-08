from decimal import Decimal
import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver
from .models import Deposit, Earnings, UserProfile, Wallet, Withdrawal

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def create_user_wallet_and_earnings(sender, instance, created, **kwargs):
    if created:
        # Create Wallet
        wallet = Wallet.objects.create(user_profile=instance)
        logger.info(f"Wallet created for user: {instance.user.username}")

        # Create Earnings with initial balance
        initial_balance = Decimal('0.00')
        Earnings.objects.create(user_profile=instance, earnings=initial_balance)
        logger.info(f"Earnings created for user: {instance.user.username} with initial balance: {initial_balance}")


@receiver(pre_delete, sender=Withdrawal)
def update_wallet_balance_on_withdrawal(sender, instance, **kwargs):
    wallet = instance.user_profile.wallet
    wallet.balance -= instance.amount
    wallet.save()
    logger.info(f"Wallet balance updated after withdrawal for user: {instance.user_profile.user.username}")
    


logger = logging.getLogger(__name__)

# deposit_approved = Signal()

# @receiver(deposit_approved)
# def update_wallet_balance(sender, deposit, **kwargs):
#     if deposit.status == 'approved':
#         try:
#             wallet = Wallet.objects.get(user=deposit.user_profile.user)
#             wallet.balance += deposit.amount
#             wallet.save()
#             logger.info(f"Wallet balance updated after deposit approval for user: {deposit.user_profile.user.username}")
#         except Wallet.DoesNotExist:
#             logger.error(f"Wallet not found for user: {deposit.user_profile.user.username} during deposit approval")
            
            
# Signal to update wallet balance when a deposit is approved
@receiver(post_save, sender=Deposit)
def update_wallet_balance(sender, instance, created, **kwargs):
    if not created and instance.status == 'approved':
        wallet = Wallet.objects.get(user_profile=instance.user_profile)
        wallet.balance += instance.amount
        wallet.save()
