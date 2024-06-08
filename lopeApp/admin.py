from django.contrib import admin
from .models import UserProfile, Wallet, Earnings, Deposit, Withdrawal

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_joined')

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'balance')

class EarningsAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'earnings', 'earned_date')

class DepositAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'amount', 'created_at', 'status')

class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'amount', 'timestamp', 'approved')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Earnings, EarningsAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)
