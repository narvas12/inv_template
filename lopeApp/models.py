from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from datetime import timedelta


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

class Wallet(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return f"Wallet of {self.user_profile.user.username}"

class Earnings(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    earned_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Earnings of {self.user_profile.user.username}"

class Deposit(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')), default='pending')

    def __str__(self):
        return f"Deposit of {self.amount} by {self.user_profile.user.username}"

class Investment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the object is being created (not updated)
            self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=5)
        super().save(*args, **kwargs)

    def check_active(self):
        if self.end_date and timezone.now() > self.end_date:
            self.is_active = False
            self.save()
        return self.is_active
    
class Withdrawal(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    wallet = models.CharField(max_length=200, default='')
    network = models.CharField(max_length=20, default='TRC20')
    timestamp = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Withdrawal of {self.amount} by {self.user_profile.user.username}"
    

class DepositConfirmation(models.Model):
    wallet_credited = models.CharField(max_length=100)
    transaction_hash = models.CharField(max_length=100)
    confirmation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Deposit Confirmation - {self.wallet_credited} - {self.transaction_hash}"



class Bonus(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_bonuses')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_bonuses')
    amount = models.DecimalField(max_digits=40, decimal_places=2)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bonus from {self.sender.username} to {self.recipient.username}"

    def process_bonus_transaction(self):
        recipient_wallet = Wallet.objects.get(user_profile=self.recipient)
        recipient_wallet.balance += Decimal(self.amount)
        recipient_wallet.save()
        
        
class Referal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referal_bonus = models.DecimalField(max_digits=40, decimal_places=2)
    
    def __str__(self) -> str:
        return f"{self.user}'s referal earnings = {self.referal_bonus}" 