from decimal import Decimal
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from lopeApp.models import Wallet, Earnings
import os

LOG_FILE_PATH = 'earnings_log.txt'

def calculate_interest_rate(balance):
    """Calculate the interest rate based on the wallet balance."""
    if 199 <= balance <= 1499:
        return Decimal('0.08') * balance
    elif 1500 <= balance <= 2999:
        return Decimal('0.10') * balance
    elif 2999 <= balance <= 5999:
        return Decimal('0.15') * balance
    elif 7000 <= balance <= 14999:
        return Decimal('0.20') * balance
    elif 15000 <= balance <= 20000:
        return Decimal('0.25') * balance
    elif 25000 <= balance <= 40000:
        return Decimal('0.20') * balance
    elif 50000 <= balance:
        return Decimal('0.40') * balance
    else:
        return Decimal('0.00')

def log_earnings_to_file(message):
    """Log earnings information to a text file."""
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"{timezone.now()}: {message}\n")

def process_wallet_earnings(wallet_id):
    print('Job started')
    """Process wallet earnings and update wallet balance."""
    try:
        wallet = Wallet.objects.get(pk=wallet_id)
        print(f"Wallet of {wallet.user_profile.user}: {wallet.balance}")
        
        interest_amount = calculate_interest_rate(wallet.balance)
        print(interest_amount)
        if interest_amount > Decimal('0'):  
            wallet.balance += interest_amount
            wallet.save()

            new_earnings = Earnings.objects.create(
                user_profile=wallet.user_profile,
                earnings=interest_amount,
                earned_date=timezone.now()
            )

            new_earnings.save()
            
            message = f"Earnings processed for user {wallet.user_profile.user} and interest earned: {interest_amount:.2f}"
            log_earnings_to_file(message)
            print(message)
        else:
            message = f"No positive interest earned for user {wallet.user_profile.user}, skipping balance update. {interest_amount:.2f}"
            log_earnings_to_file(message)
            print(message)
    except Exception as e:
        error_message = f"Error processing wallet {wallet_id}: {str(e)}"
        log_earnings_to_file(error_message)
        print(error_message)

def start():
    scheduler = BackgroundScheduler()
    jobs = scheduler.get_jobs()

    scheduled_wallet_ids = set(job.args[0] for job in jobs)

    wallets = Wallet.objects.all()
    
    for wallet in wallets:
        if wallet.pk not in scheduled_wallet_ids:
            if 199 <= wallet.balance <= 1499 or 2999 <= wallet.balance <= 5999 or 15000 <= wallet.balance <= 20000:

                scheduler.add_job(process_wallet_earnings, 'interval', hours=24, args=[wallet.pk])
            elif 1500 <= wallet.balance <= 2999 or 7000 <= wallet.balance <= 14999:

                scheduler.add_job(process_wallet_earnings, 'interval', hours=20, args=[wallet.pk])
            elif 25000 <= wallet.balance <= 40000:

                scheduler.add_job(process_wallet_earnings, 'interval', hours=48, args=[wallet.pk])
            elif 50000 <= wallet.balance:

                scheduler.add_job(process_wallet_earnings, 'interval', hours=72, args=[wallet.pk])
    
    scheduler.start()

if __name__ == "__main__":
    start()
