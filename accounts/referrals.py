# accounts/referrals.py
from .models import Commission, UserPlan, CommissionRate, Plan
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

def get_commission_rate(seller_plan, sold_plan, level):
    """
    Get commission rate based on seller plan, sold plan and level
    """
    try:
        rate_config = CommissionRate.objects.get(
            seller_plan=seller_plan, 
            sold_plan=sold_plan, 
            is_active=True
        )
        
        if level == 1:
            return rate_config.level_1_percentage
        elif level == 2:
            return rate_config.level_2_percentage
        elif level == 3:
            return rate_config.level_3_percentage
        else:
            return Decimal('0.00')
            
    except CommissionRate.DoesNotExist:
        # Default rates if no configuration found
        default_rates = {1: Decimal('40.00'), 2: Decimal('8.00'), 3: Decimal('2.00')}
        return default_rates.get(level, Decimal('0.00'))

def calculate_commission_amount(plan_price, percentage_rate):
    """
    Calculate commission amount based on plan price and percentage
    """
    try:
        return (Decimal(str(plan_price)) * percentage_rate) / 100
    except Exception:
        return Decimal('0.00')

@transaction.atomic
def handle_successful_payment(payment):
    """
    Award commission to referrer(s) when a payment is approved
    """
    if not payment.plan:
        return
    
    user = payment.user
    sold_plan = payment.plan
    
    # Get buyer's current plan for determining commission rates
    try:
        buyer_profile = user.userprofile
        buyer_plan = buyer_profile.plan
    except:
        buyer_plan = 'NONE'
    
    level = 1
    referrer = getattr(user.userprofile, 'referred_by', None) if hasattr(user, 'userprofile') else None

    while referrer and level <= 3:
        # Get referrer's plan
        try:
            referrer_plan = referrer.userprofile.plan
        except:
            referrer_plan = 'NONE'
        
        # Get commission rate for this scenario
        percentage_rate = get_commission_rate(referrer_plan, sold_plan, level)
        
        # Calculate commission amount
        commission_amount = calculate_commission_amount(sold_plan.price, percentage_rate)
        
        if commission_amount > 0:
            Commission.objects.create(
                user=referrer,
                referred_user=user,
                sold_plan=sold_plan,
                seller_plan=referrer_plan,
                level=level,
                percentage_rate=percentage_rate,
                amount=commission_amount,
                payment=payment
            )
        
        # Move up the referral chain
        if hasattr(referrer, 'userprofile'):
            referrer = referrer.userprofile.referred_by
        else:
            referrer = None
        level += 1

def get_user_commission_summary(user):
    """
    Get commission summary for a user
    """
    commissions = Commission.objects.filter(user=user)
    
    summary = {
        'total_commission': sum(c.amount for c in commissions),
        'level_1_commission': sum(c.amount for c in commissions if c.level == 1),
        'level_2_commission': sum(c.amount for c in commissions if c.level == 2),
        'level_3_commission': sum(c.amount for c in commissions if c.level == 3),
        'total_referrals': commissions.count(),
        'commission_breakdown': {}
    }
    
    # Group by sold plans
    for plan in Plan.objects.all():
        plan_commissions = commissions.filter(sold_plan=plan)
        if plan_commissions.exists():
            summary['commission_breakdown'][plan.name] = {
                'total': sum(c.amount for c in plan_commissions),
                'count': plan_commissions.count()
            }
    
    return summary

# Backward compatibility function for admin actions
def handle_successful_referral(user):
    """
    Legacy function for backward compatibility
    Creates commission based on user's latest plan purchase
    """
    user_plan = UserPlan.objects.filter(user=user).order_by('-purchase_date').first()
    if not user_plan:
        return
    
    # Create a dummy payment object for the new commission system
    from .models import Payment
    
    # Check if there's an existing payment for this user and plan
    payment = Payment.objects.filter(
        user=user, 
        plan=user_plan.plan, 
        status='approved'
    ).first()
    
    if payment:
        # Use existing payment
        handle_successful_payment(payment)
    else:
        # Create a temporary payment record for commission calculation
        payment = Payment.objects.create(
            user=user,
            plan=user_plan.plan,
            amount=user_plan.plan.price,
            status='approved'
        )
        handle_successful_payment(payment)


@transaction.atomic  
def calculate_commissions_for_plan_upgrade(user, new_plan_name):
    """
    Calculate commissions when admin upgrades a user's plan from NONE to a paid plan.
    This replaces the payment-based commission system.
    """
    try:
        # Get the plan object - prefer the uppercase version first
        try:
            plan = Plan.objects.get(name=new_plan_name.upper())
        except Plan.DoesNotExist:
            plan = Plan.objects.get(name__iexact=new_plan_name)
    except Plan.DoesNotExist:
        print(f"Plan '{new_plan_name}' not found")
        return
    except Plan.MultipleObjectsReturned:
        # If multiple plans exist, prefer the uppercase version
        plan = Plan.objects.filter(name=new_plan_name.upper()).first()
        if not plan:
            plan = Plan.objects.filter(name__iexact=new_plan_name).first()

    # Get user's referral information  
    try:
        user_profile = user.userprofile
        if not user_profile.referred_by:
            print(f"User {user.username} was not referred by anyone")
            return
    except:
        print(f"No profile found for user {user.username}")
        return

    print(f"Calculating commissions for {user.username} upgrading to {plan.name}")

    # Get referral chain
    referral_chain = []
    current_referrer = user_profile.referred_by
    level = 1

    while current_referrer and level <= 3:
        try:
            referrer_profile = current_referrer.userprofile
            # Only give commission if referrer has a paid plan (not NONE)
            if referrer_profile.plan != 'NONE':
                referral_chain.append((current_referrer, level, referrer_profile.plan))
            
            # Move up the chain
            current_referrer = referrer_profile.referred_by
            level += 1
        except:
            break

    print(f"Found referral chain: {referral_chain}")

    # Calculate commissions for each level
    for referrer, level, referrer_plan_name in referral_chain:
        try:
            # Get referrer's plan object - prefer uppercase version first
            try:
                referrer_plan = Plan.objects.get(name=referrer_plan_name.upper())
            except Plan.DoesNotExist:
                referrer_plan = Plan.objects.get(name__iexact=referrer_plan_name)
        except Plan.DoesNotExist:
            print(f"Referrer plan '{referrer_plan_name}' not found")
            continue
        except Plan.MultipleObjectsReturned:
            # If multiple plans exist, prefer the uppercase version
            referrer_plan = Plan.objects.filter(name=referrer_plan_name.upper()).first()
            if not referrer_plan:
                referrer_plan = Plan.objects.filter(name__iexact=referrer_plan_name).first()

        # Get commission rate
        percentage_rate = get_commission_rate(referrer_plan, plan, level)
        commission_amount = calculate_commission_amount(plan.price, percentage_rate)

        if commission_amount > 0:
            # Create commission record
            commission = Commission.objects.create(
                user=referrer,
                referred_user=user,
                sold_plan=plan,
                level=level,
                percentage_rate=percentage_rate,
                amount=commission_amount
            )
            print(f"Created commission: {referrer.username} gets Rs.{commission_amount} from {user.username} (Level {level})")
        else:
            print(f"No commission for {referrer.username} at level {level}")

    print(f"Commission calculation completed for {user.username}")


@transaction.atomic
def handle_referral_chain_change(user, old_referred_by, new_referred_by, user_plan):
    """
    Handle when admin changes the referred_by field in UserProfile.
    This maintains commission history while noting the change.
    """
    print(f"Handling referral chain change for {user.username}")
    print(f"  Old referrer: {old_referred_by.username if old_referred_by else 'None'}")
    print(f"  New referrer: {new_referred_by.username if new_referred_by else 'None'}")
    print(f"  User plan: {user_plan}")
    
    # If user has a paid plan, we need to handle existing commissions
    if user_plan != 'NONE':
        
        # Mark existing commissions as "referral changed" by adding a note
        # We don't delete them to maintain audit trail
        existing_commissions = Commission.objects.filter(referred_user=user, is_active=True)
        
        if existing_commissions.exists():
            print(f"  Found {existing_commissions.count()} existing active commissions")
            
            # Mark existing commissions as inactive and add admin note
            for comm in existing_commissions:
                comm.is_active = False
                comm.admin_note = f"Referral chain changed on {timezone.now().date()}. Old referrer: {old_referred_by.username if old_referred_by else 'None'}, New referrer: {new_referred_by.username if new_referred_by else 'None'}"
                comm.save()
                print(f"    Marked inactive: {comm.user.username} -> Rs.{comm.amount} (was Level {comm.level})")
        
        # If user now has a new referrer and a paid plan, calculate new commissions
        if new_referred_by and user_plan != 'NONE':
            print(f"  Calculating new commissions for new referral chain...")
            
            # Get the plan object for commission calculation
            try:
                plan = Plan.objects.filter(name=user_plan.upper()).first()
                if not plan:
                    plan = Plan.objects.filter(name__iexact=user_plan).first()
                    
                if plan:
                    # Calculate new referral chain commissions
                    referral_chain = []
                    current_referrer = new_referred_by
                    level = 1

                    while current_referrer and level <= 3:
                        try:
                            referrer_profile = current_referrer.userprofile
                            if referrer_profile.plan != 'NONE':
                                referral_chain.append((current_referrer, level, referrer_profile.plan))
                            current_referrer = referrer_profile.referred_by
                            level += 1
                        except:
                            break

                    print(f"  New referral chain: {referral_chain}")

                    # Create new commissions for the new chain
                    for referrer, level, referrer_plan_name in referral_chain:
                        try:
                            referrer_plan = Plan.objects.filter(name=referrer_plan_name.upper()).first()
                            if not referrer_plan:
                                referrer_plan = Plan.objects.filter(name__iexact=referrer_plan_name).first()
                                
                            if referrer_plan:
                                percentage_rate = get_commission_rate(referrer_plan, plan, level)
                                commission_amount = calculate_commission_amount(plan.price, percentage_rate)

                                if commission_amount > 0:
                                    # Check if ACTIVE commission already exists for this combination
                                    existing = Commission.objects.filter(
                                        user=referrer,
                                        referred_user=user,
                                        sold_plan=plan,
                                        level=level,
                                        is_active=True
                                    ).exists()
                                    
                                    if not existing:
                                        commission = Commission.objects.create(
                                            user=referrer,
                                            referred_user=user,
                                            sold_plan=plan,
                                            level=level,
                                            percentage_rate=percentage_rate,
                                            amount=commission_amount
                                        )
                                        print(f"  Created NEW commission: {referrer.username} gets Rs.{commission_amount} (Level {level})")
                                    else:
                                        print(f"  Commission already exists for {referrer.username} at level {level}")
                        except Exception as e:
                            print(f"  Error creating commission for {referrer.username}: {e}")
                            
            except Exception as e:
                print(f"  Error finding plan {user_plan}: {e}")
    
    print(f"Referral chain change handling completed for {user.username}")
