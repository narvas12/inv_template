from decimal import Decimal
import time
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from core import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Bonus, DepositConfirmation, Investment, Referal, UserProfile, Wallet, Deposit, Withdrawal, Earnings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SpendFundForm, UserRegistrationForm, UserLoginForm
from django.contrib.auth import logout
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Sum
from django_user_agents.utils import get_user_agent
from ipware import get_client_ip
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives



def home(request):
    return render(request, 'index.html')


def base(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    username = user_profile.user.username
    context = {
        'username':username
    }
    return render(request, 'auth_base.html', context)


def about(request):
    return render(request, 'about.html')


def plans(request):
    return render(request, 'plans/plans.html')

# @login_required
def manager(request):
    return render(request, 'management/manager.html')


@login_required
def auth_plans(request):
    return render(request, 'plans/auth_plans.html')

def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('phone')
        message = request.POST.get('message')

        if not name or not email or not subject or not message:
            messages.error(request, 'Please fill in all fields.')
            return redirect('contact_form')

        email_message = render_to_string('email_templates/message.html', {'name': name, 'email': email, 'message': message})

        send_mail(
            subject,
            '',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            html_message=email_message,
            fail_silently=True
        )

        messages.success(request, 'Message sent successfully!')
        return redirect('home')
    else:
        return render(request, 'contact.html')
    



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            send_user_welcome_message(user)

            ip, _ = get_client_ip(request)
            user_agent = get_user_agent(request)
            device_type = user_agent.device.family if user_agent.is_mobile else 'Unknown'

            send_company_notification(user, ip, user_agent.os.family, device_type)

            return redirect('registration_success')  
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            return render(request, 'authentication/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})



def send_user_welcome_message(user):
    subject = 'Welcome to Our Website!'
    sender_email = settings.EMAIL_HOST_USER 

    html_message = render_to_string('email_templates/welcome_email.html', {'user': user})
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        sender_email,
        [user.email],
        html_message=html_message,
        fail_silently=True
    )

def send_company_notification(user, ip, country, device_type):
    subject = 'New User Registration Notification'
    sender_email = settings.EMAIL_HOST_USER 

    message = f'A new user has registered on the website.\n\nUsername: {user.username}\nEmail: {user.email}\nIP Address: {ip}\nCountry: {country}\nDevice Type: {device_type}'
    
    send_mail(
        subject,
        message,
        sender_email,
        [settings.EMAIL_HOST_USER], 
        fail_silently=True
    )


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('login_success')  # Redirect to the home page after successful login
            else:
                messages.error(request, "Invalid username or password.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = UserLoginForm()
    return render(request, 'authentication/login.html', {'form': form})





def login_success_view(request):
    return render(request, 'authentication/login_success.html')

def registration_success_view(request):
    return render(request, 'authentication/registration_success.html')


def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def deposit_view(request):
    username = request.user
    if request.method == 'POST':
        amount = request.POST.get('amount')
        plan = request.POST.get('membership_level')
        if amount:
            deposit = Deposit.objects.create(user_profile=request.user.userprofile, amount=amount)
            deposit.save()

            time.sleep(3)

            send_deposit_email(request.user, amount, plan)
            send_deposit_notification_email(request.user, amount, plan)

            return redirect('deposit_success')
    return render(request, 'transactions/deposit.html', {'username':username})


def send_deposit_email(user, amount, plan):
    subject = 'Deposit Initiated'
    sender_email = 'billing@polkavite.com' 

    html_message = render_to_string('email_templates/deposit_initiation_email.html', {'user': user, 'amount': amount, 'membership_level':plan})

    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, sender_email, [user.email], html_message=html_message, fail_silently=True)
    

def send_deposit_notification_email(user, amount, plan):
    subject = 'Deposit Initiated'
    sender_email = 'billing@polkavite.com' 

    html_message = render_to_string('email_templates/deposit_initiation_email.html', {'user': user, 'amount': amount, 'membership_level':plan})

    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, sender_email, [settings.EMAIL_HOST_USER], html_message=html_message)


def deposit_success_view(request):
    return render(request, 'transactions/deposit_success.html')



def confirm_deposit(request):
    username = request.user
    if request.method == 'POST':
        wallet_credited = request.POST.get('wallet_credited')
        transaction_hash = request.POST.get('transaction_hash')

        if not wallet_credited or not transaction_hash:
            messages.error(request, 'Please provide wallet credited and transaction hash.')
            return redirect('confirm_deposit')

        deposit_confirmation = DepositConfirmation.objects.create(
            wallet_credited=wallet_credited,
            transaction_hash=transaction_hash
        )
        deposit_confirmation.save()

        send_confirmation_email(request.user, wallet_credited, transaction_hash)

        messages.success(request, 'Deposit confirmed successfully!')
        return redirect('deposit_confirmation_success')  
    else:
        return render(request, 'transactions/confirmations/confirm_deposit.html', {'username':username}) 



def send_confirmation_email(user, wallet_credited, transaction_hash):
    subject = 'Deposit Confirmation'
    sender_email = 'billing@polkavite.com'  

    html_message = render_to_string('email_templates/deposit_approval_request_email.html', {
        'user': user,
        'wallet_credited': wallet_credited,
        'transaction_hash': transaction_hash
    })

    send_mail(
        subject,
        strip_tags(html_message), 
        sender_email,
        [settings.EMAIL_HOST_USER],
        html_message=html_message,
        fail_silently=True
    )


    

def deposit_confirmation_success(request):
    return render(request, 'transactions/deposit_cpnfirmation_success.html')



from decimal import Decimal  # Import Decimal for handling decimal values

@login_required
def withdrawal_view(request):
    username = request.user
    if request.method == 'POST':
        amount_str = request.POST.get('amount') 
        wallet = request.POST.get('wallet')
        network = request.POST.get('network')

        if amount_str and wallet and network:
            amount = Decimal(amount_str) 
            user_profile = request.user.userprofile
            
            wallet_balance = user_profile.wallet.balance
            if wallet_balance >= amount:
                withdrawal = Withdrawal.objects.create(
                    user_profile=user_profile,
                    amount=amount,
                    wallet=wallet,
                    network=network
                )
                withdrawal.save()

                user_profile.wallet.balance -= amount
                user_profile.wallet.save()

                send_user_withdrawal_notification(request.user, withdrawal)

                notify_company_withdrawal(withdrawal)

                return redirect('withdrawal_success') 
            else:
                messages.error(request, 'Insufficient balance in your wallet.')
                
        else:
            messages.error(request, 'Please provide all required information.')
    else:
        messages.error(request, 'Invalid request method.')

    # Get the user's wallet balance as context
    user_profile = request.user.userprofile
    wallet_balance = user_profile.wallet.balance
    
    return render(request, 'transactions/withdrawal.html', {'wallet_balance': wallet_balance, 'username':username})


def send_user_withdrawal_notification(user, withdrawal):
    subject = 'Withdrawal Request Confirmation'
    sender_email = 'billing@polkavite.com'  # Update with your email

    html_message = render_to_string('email_templates/withdrawal_user_notification.html', {'user': user, 'withdrawal': withdrawal})
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        sender_email,
        [user.email],
        html_message=html_message,
        fail_silently=True
    )

def notify_company_withdrawal(withdrawal):
    subject = 'New Withdrawal Request'
    sender_email = 'billing@okxgurad.com'  # Update with your email

    html_message = render_to_string('email_templates/withdrawal_company_notification.html', {'withdrawal': withdrawal})
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        sender_email,
        [settings.EMAIL_HOST_USER],
        html_message=html_message,
        fail_silently=True
    )

def withdrawal_success(request):
    return render(request, 'transactions/withdrawal_success.html')




@login_required
def dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    username = user_profile.user.username

    approved_deposits_total = Deposit.objects.filter(user_profile=user_profile, status='approved').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    has_deposits = approved_deposits_total > Decimal('0.00')

    earnings_total = Earnings.objects.filter(user_profile=user_profile).aggregate(Sum('earnings'))['earnings__sum'] or Decimal('0.00')
    has_earnings = earnings_total > Decimal('0.00')

    approved_withdrawals_total = Withdrawal.objects.filter(user_profile=user_profile, approved=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    has_withdrawals = approved_withdrawals_total > Decimal('0.00')

    wallet_balance = user_profile.wallet.balance - approved_withdrawals_total if hasattr(user_profile, 'wallet') else Decimal('0.00')
    has_wallet = hasattr(user_profile, 'wallet') and wallet_balance > Decimal('0.00')

    pending_withdrawals_total = Withdrawal.objects.filter(user_profile=user_profile, approved=False).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    has_pending_withdrawals = pending_withdrawals_total > Decimal('0.00')

    total_earnings = earnings_total

    try:
        referal = Referal.objects.get(user=request.user)
        referal_bonus = referal.referal_bonus
        has_referal = True
    except Referal.DoesNotExist:
        referal_bonus = Decimal(0)
        has_referal = False

    active_investments = Investment.objects.filter(user_profile=user_profile, is_active=True)
    total_active_investments = active_investments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    has_active_investments = total_active_investments > Decimal('0.00')

    context = {
        'approved_deposits_total': approved_deposits_total,
        'wallet_balance': wallet_balance,
        'pending_withdrawals_total': pending_withdrawals_total,
        'total_earnings': total_earnings,
        'username': username,
        'referal_bonus': referal_bonus,
        'total_active_investments': total_active_investments,
        'has_deposits': has_deposits,
        'has_earnings': has_earnings,
        'has_withdrawals': has_withdrawals,
        'has_wallet': has_wallet,
        'has_pending_withdrawals': has_pending_withdrawals,
        'has_referal': has_referal,
        'has_active_investments': has_active_investments,
    }

    return render(request, 'accounts/dashboard.html', context)



@login_required
def earning_history(request):
    username = request.user
    user_profile = request.user.userprofile

    earnings_history = Earnings.objects.filter(user_profile=user_profile).order_by('-earned_date')

    context = {
        'user_profile': user_profile,
        'earnings_history': earnings_history,
        'username':username
    }
    return render(request, 'transactions/earning_history.html', context)



def deposit_history(request):
    username = request.user
    user_profile = request.user.userprofile
    deposits = Deposit.objects.filter(user_profile=user_profile).order_by('-created_at')
    return render(request, 'transactions/deposit_history.html', {'deposits': deposits, 'username':username})


def withdrawal_history(request):
    username = request.user
    user_profile = request.user.userprofile
    withdrawals = Withdrawal.objects.filter(user_profile=user_profile).order_by('-timestamp')
    return render(request, 'transactions/withdrawal_history.html', {'withdrawals': withdrawals, 'username':username})



def manage_deposits(request):
    if request.method == 'POST':
        selected_deposits = request.POST.getlist('selected_deposits')
        pending_deposits = Deposit.objects.filter(id__in=selected_deposits, status='pending')

        for deposit in pending_deposits:
            deposit.status = 'approved'
            deposit.save()

        approved_count = pending_deposits.count()

        context = {
            'deposits': pending_deposits,
            'approved_count': approved_count,
            'username': request.user,
            'message': f"{approved_count} deposit(s) approved successfully."
        }

        return render(request, 'management/manage_deposits.html', context)

    pending_deposits = Deposit.objects.filter(status='pending')
    context = {
        'deposits': pending_deposits,
        'approved_count': 0,  # Initialize approved count to 0 initially
        'username': request.user
    }

    return render(request, 'management/manage_deposits.html', context)



def manage_withdrawals(request):
    username = request.user
    if request.method == 'POST':
        withdrawal_ids = request.POST.getlist('withdrawal_ids')
        if withdrawal_ids:
            Withdrawal.objects.filter(id__in=withdrawal_ids).update(approved=True)

            approved_withdrawals = Withdrawal.objects.filter(id__in=withdrawal_ids)
            for withdrawal in approved_withdrawals:
                send_withdrawal_confirmation_email(withdrawal)

            messages.success(request, 'Selected withdrawals approved successfully.')
            return redirect('manage_withdrawals')

    withdrawals = Withdrawal.objects.all()

    context = {
        'withdrawals': withdrawals,
        'username':username
    }
    return render(request, 'management/manage_withdrawals.html', context)



def send_withdrawal_confirmation_email(withdrawal):
    subject = 'Withdrawal Approved'
    recipient_email = withdrawal.user_profile.user.email
    
    email_message = render_to_string('email_templates/withdrawal_confirmation_email.html', {'withdrawal': withdrawal})
    
    email = EmailMessage(subject, email_message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
    
    email.content_subtype = 'html'
    
    email.send()




@login_required
def send_bonus(request):
    username = request.user
    if request.method == 'POST':
        amount = request.POST.get('amount')
        recipient_username = request.POST.get('recipient_username')

        try:
            recipient_profile = UserProfile.objects.get(user__username=recipient_username)
            print(f"Recipient Profile: {recipient_profile}")  # Debugging print statement
            print(f"Recipient User: {recipient_profile.user}")  # Debugging print statement
        except UserProfile.DoesNotExist:
            messages.error(request, f"User with username '{recipient_username}' not found.")
            return redirect('send_bonus')

        sender = request.user 
        bonus = Bonus.objects.create(sender=sender, recipient=recipient_profile, amount=amount)
        bonus.process_bonus_transaction()
        
        send_bonus_confirmation_email(sender, recipient_profile.user, amount)
        messages.success(request, f"Bonus of ${amount} sent successfully to {recipient_username}.")
        return redirect('send_bonus')

    all_users = UserProfile.objects.all()
    return render(request, 'transactions/send_bonus.html', {'all_users': all_users, 'username':username})




def send_bonus_confirmation_email(sender, recipient, amount):
    subject = 'Bonus Awarded'

    email_message = render_to_string('email_templates/bonus_confirmation_email.html', {'recipient': recipient, 'amount': amount, 'sender': sender})

    email = EmailMessage(subject, email_message, settings.DEFAULT_FROM_EMAIL, [recipient.email])

    email.content_subtype = 'html'

    email.send()

    
    

@login_required
def referal(request, username):
    try:
        referal = Referal.objects.get(user=request.user)
        referal_bonus = referal.referal_bonus
    except Referal.DoesNotExist:
        referal_bonus = 0
    
    return redirect('register')



def send_email(user, subject, template_name, from_email):
    html_content = render_to_string(template_name, {'user': user})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

def send_monthly_offer(request):
    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        users = User.objects.filter(id__in=selected_users)
        
        for user in users:
            send_email(
                user=user,
                subject='Special Monthly Offer',
                template_name='email_templates/monthly_offer.html',
                from_email='offers@polkavite.com'
            )

        messages.success(request, 'Monthly offers have been sent successfully.')
        return redirect('send_monthly_offer')

    users = User.objects.all()
    return render(request, 'management/send_monthly_offer.html', {'users': users})



def send_new_month_message(request):
    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        users = User.objects.filter(id__in=selected_users)
        
        for user in users:
            send_email(
                user=user,
                subject='Happy New Month',
                template_name='email_templates/send_new_month_message.html',
                from_email='admin@polkavite.com'
            )

        messages.success(request, 'Messages have been sent successfully.')
        return redirect('send_new_month_message')

    users = User.objects.all()
    return render(request, 'management/send_new_month_message.html', {'users': users})




@login_required
def spend_fund(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    wallet_balance = user_profile.wallet.balance if hasattr(user_profile, 'wallet') else Decimal('0.00')
    
    # Calculate total earnings
    earnings_total = Earnings.objects.filter(user_profile=user_profile).aggregate(Sum('earnings'))['earnings__sum'] or Decimal('0.00')

    if request.method == 'POST':
        form = SpendFundForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if earnings_total >= amount:
                # Deduct the amount from wallet balance
                user_profile.wallet.balance -= amount
                user_profile.wallet.save()

                # Create an active investment
                Investment.objects.create(
                    user_profile=user_profile,
                    amount=amount,
                    is_active=True
                )

                messages.success(request, f'You have successfully invested ${amount}.')
                return redirect('dashboard')
            else:
                form.add_error('amount', 'Insufficient earnings')
    else:
        form = SpendFundForm()

    context = {
        'form': form,
        'wallet_balance': wallet_balance,
        'earnings_total': earnings_total,
    }

    return render(request, 'transactions/spend_fund.html', context)