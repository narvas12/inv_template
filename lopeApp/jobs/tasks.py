from decimal import Decimal
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from lopeApp.models import Wallet, Earnings

def calculate_interest_rate(balance):
    """Calculate the interest rate based on the wallet balance."""
    if 200 <= balance <= 999:
        return Decimal('0.08') * balance
    elif 1000 <= balance <= 2999:
        return Decimal('0.10') * balance
    elif 3000 <= balance <= 5999:
        return Decimal('0.13') * balance
    elif 7000 <= balance <= 14000:
        return Decimal('0.18') * balance
    elif 15000 <= balance <= 20000:
        return Decimal('0.23') * balance
    elif 25000 <= balance <= 40000:
        return Decimal('0.28') * balance
    elif 50000 <= balance:
        return Decimal('0.33') * balance
    else:
        return Decimal('0.00')

def process_wallet_earnings(wallet_id):
    print('job started')
    """Process wallet earnings and update wallet balance."""
    wallet = Wallet.objects.get(pk=wallet_id)
    print(f"Wallet of {wallet.user_profile.user} {wallet.balance}")
    
    interest_amount = calculate_interest_rate(wallet.balance)
    print(interest_amount)
    if interest_amount > Decimal('0'):  
        wallet.balance += interest_amount
        wallet.save()

        # Create a new Earnings instance for this wallet
        new_earnings = Earnings.objects.create(
            user_profile=wallet.user_profile,
            earnings=interest_amount,
            earned_date=timezone.now()
        )
    
        print(f"Earnings processed for user {wallet.user_profile.user} and interest earned: {interest_amount:.2f}")
    else:
        print(f"No positive interest earned {wallet.user_profile.user}, skipping balance update. {interest_amount:.2f}")

def start():
    scheduler = BackgroundScheduler()
    jobs = scheduler.get_jobs()  # Get all currently scheduled jobs
    
    # Get a set of wallet IDs for which jobs are already scheduled
    scheduled_wallet_ids = set(job.args[0] for job in jobs)
    
    # Get all wallets
    wallets = Wallet.objects.all()
    
    for wallet in wallets:
        if wallet.pk not in scheduled_wallet_ids:  # Check if job already exists for this wallet
            scheduler.add_job(process_wallet_earnings, 'interval', seconds=5, args=[wallet.pk])
    
    scheduler.start()

# Ensure the scheduler is started when the script is run
if __name__ == "__main__":
    start()
