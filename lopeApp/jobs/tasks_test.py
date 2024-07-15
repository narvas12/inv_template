from decimal import Decimal
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from lopeApp.models import Wallet, Earnings, Investment
import os

LOG_FILE_PATH = 'earnings_log.txt'

def calculate_interest_rate(investment_amount):
    """Calculate the interest rate based on the investment amount."""
    if 199 <= investment_amount <= 1499:
        return Decimal('0.08') * investment_amount
    elif 1500 <= investment_amount <= 2999:
        return Decimal('0.10') * investment_amount
    elif 2999 <= investment_amount <= 5999:
        return Decimal('0.15') * investment_amount
    elif 7000 <= investment_amount <= 14999:
        return Decimal('0.20') * investment_amount
    elif 15000 <= investment_amount <= 20000:
        return Decimal('0.25') * investment_amount
    elif 25000 <= investment_amount <= 40000:
        return Decimal('0.20') * investment_amount
    elif 50000 <= investment_amount:
        return Decimal('0.40') * investment_amount
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
        active_investments = Investment.objects.filter(user_profile=wallet.user_profile, is_active=True)
        total_investment_amount = sum(investment.amount for investment in active_investments)

        interest_amount = calculate_interest_rate(total_investment_amount)
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
            active_investments = Investment.objects.filter(user_profile=wallet.user_profile, is_active=True)
            total_investment_amount = sum(investment.amount for investment in active_investments)
            
            if 199 <= total_investment_amount <= 1499 or 2999 <= total_investment_amount <= 5999 or 15000 <= total_investment_amount <= 20000:
                scheduler.add_job(
                    process_wallet_earnings,
                    'interval',
                    seconds=5,
                    args=[wallet.pk]
                )
            elif 1500 <= total_investment_amount <= 2999 or 7000 <= total_investment_amount <= 14999 or 25000 <= total_investment_amount <= 40000:
                scheduler.add_job(
                    process_wallet_earnings,
                    'interval',
                    seconds=10,
                    args=[wallet.pk]
                )
            elif total_investment_amount >= 50000:
                scheduler.add_job(
                    process_wallet_earnings,
                    'interval',
                    seconds=15,
                    args=[wallet.pk]
                )
            elif total_investment_amount < 199:
                scheduler.add_job(
                    process_wallet_earnings,
                    'interval',
                    seconds=20,
                    args=[wallet.pk]
                )

    scheduler.start()
