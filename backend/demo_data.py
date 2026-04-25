#!/usr/bin/env python
"""
Create comprehensive demo data for AI-powered analytics
Generates 120 days of realistic data with trends for ML predictions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from core.models import Influencer, Sale, Click, Campaign
from payments.models import Payment, BankAccount
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()

print("="*60)
print("Creating AI-Ready Demo Data (120 days of realistic data)")
print("="*60)

# Clear existing data (optional - comment out if you want to keep existing)
# print("\nClearing existing demo data...")
# Payment.objects.all().delete()
# Sale.objects.all().delete()
# Click.objects.all().delete()
# Influencer.objects.filter(user__email__contains='@demo.com').delete()
# User.objects.filter(email__contains='@demo.com').delete()

# 1. Create Multiple Campaigns
print("\n1. Creating Campaigns...")
campaigns_data = [
    {'name': 'Summer Sale 2024', 'url': 'https://example.com/summer-sale', 'commission': 15},
    {'name': 'Back to School', 'url': 'https://example.com/back-to-school', 'commission': 12},
    {'name': 'Holiday Special', 'url': 'https://example.com/holiday', 'commission': 20},
    {'name': 'New Year Launch', 'url': 'https://example.com/new-year', 'commission': 18},
]

campaigns = []
for camp_data in campaigns_data:
    campaign, _ = Campaign.objects.get_or_create(
        name=camp_data['name'],
        defaults={
            'product_url': camp_data['url'],
            'commission_rate': Decimal(str(camp_data['commission'])),
            'is_active': True
        }
    )
    campaigns.append(campaign)
    print(f"   ✓ {campaign.name} ({camp_data['commission']}% commission)")

# 2. Create 8 Influencers with Different Performance Profiles
print("\n2. Creating Influencers with Performance Profiles...")

influencers_config = [
    # Top Performer - High growth trend
    {'email': 'alice@demo.com', 'username': 'alice_style', 'bio': 'Fashion & Lifestyle', 
     'social': '@alice_style', 'base_clicks': 150, 'growth_rate': 0.02, 'conversion': 0.25},
    
    # Tech Reviewer - Steady performance
    {'email': 'bob@demo.com', 'username': 'bob_tech', 'bio': 'Tech Reviews', 
     'social': '@bobtech', 'base_clicks': 80, 'growth_rate': 0.01, 'conversion': 0.20},
    
    # Fitness - Seasonal peaks (weekends higher)
    {'email': 'carol@demo.com', 'username': 'carol_fit', 'bio': 'Fitness & Health', 
     'social': '@carolfit', 'base_clicks': 120, 'growth_rate': 0.015, 'conversion': 0.22},
    
    # Food Blogger - Weekday focused
    {'email': 'dave@demo.com', 'username': 'dave_food', 'bio': 'Food & Cooking', 
     'social': '@davecooks', 'base_clicks': 90, 'growth_rate': 0.005, 'conversion': 0.18},
    
    # Travel - Irregular spikes (holiday effect)
    {'email': 'eve@demo.com', 'username': 'eve_travel', 'bio': 'Travel Blogger', 
     'social': '@evetravels', 'base_clicks': 200, 'growth_rate': 0.03, 'conversion': 0.15},
    
    # Newcomer - Low base but high growth
    {'email': 'frank@demo.com', 'username': 'frank_gaming', 'bio': 'Gaming Content', 
     'social': '@frankgames', 'base_clicks': 30, 'growth_rate': 0.08, 'conversion': 0.12},
    
    # Established - Consistent
    {'email': 'grace@demo.com', 'username': 'grace_beauty', 'bio': 'Beauty & Skincare', 
     'social': '@gracebeauty', 'base_clicks': 100, 'growth_rate': 0.008, 'conversion': 0.28},
    
    # Declining - For trend analysis
    {'email': 'henry@demo.com', 'username': 'henry_music', 'bio': 'Music Reviews', 
     'social': '@henrymusic', 'base_clicks': 70, 'growth_rate': -0.01, 'conversion': 0.10},
]

# IP addresses for realistic fraud detection patterns
ip_pools = {
    'normal': [f'192.168.1.{i}' for i in range(1, 100)],
    'suspicious': ['10.0.0.1', '10.0.0.2', '10.0.0.3'],  # Same IP many clicks
    'mobile': ['172.16.0.' + str(i) for i in range(1, 50)],
    'international': ['203.0.113.' + str(i) for i in range(1, 30)],
}

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148',
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/119.0.0.0 Mobile Safari/537.36',
]

today = timezone.now()
influencers = []

for i, config in enumerate(influencers_config, 1):
    # Create user
    user, created = User.objects.get_or_create(
        email=config['email'],
        defaults={
            'username': config['username'],
            'role': 'influencer',
            'phone': f'+1-555-{random.randint(1000, 9999)}'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
    
    # Create influencer profile
    commission_rate = Decimal(str(random.randint(10, 25)))
    influencer, _ = Influencer.objects.get_or_create(
        user=user,
        defaults={
            'commission_rate': commission_rate,
            'bio': config['bio'],
            'social_handle': config['social'],
            'is_active': True,
            'total_earnings': Decimal('0'),
            'pending_amount': Decimal('0')
        }
    )
    influencers.append(influencer)
    
    # Create bank account for payments
    BankAccount.objects.get_or_create(
        influencer=influencer,
        defaults={
            'account_holder': config['username'].replace('_', ' ').title(),
            'account_number': f'{random.randint(10000000, 99999999)}',
            'bank_name': random.choice(['Chase', 'Bank of America', 'Wells Fargo', 'Citi']),
            'ifsc_code': f'IFSC{random.randint(10000, 99999)}',
            'is_verified': True
        }
    )
    
    # Generate 120 days of realistic data
    total_clicks = 0
    total_sales = 0
    total_earnings = Decimal('0')
    total_pending = Decimal('0')
    
    for day_offset in range(120, 0, -1):
        date = today - timedelta(days=day_offset)
        
        # Calculate daily clicks with growth trend and day-of-week variation
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        weekend_boost = 1.3 if day_of_week >= 5 else 1.0
        
        # Apply growth trend over time
        days_active = 120 - day_offset
        growth_multiplier = 1 + (days_active * config['growth_rate'])
        
        # Base daily clicks with some randomness
        daily_clicks = int(config['base_clicks'] / 30 * growth_multiplier * weekend_boost)
        daily_clicks = max(1, int(daily_clicks * random.uniform(0.7, 1.3)))  # Add variance
        
        # Generate clicks for this day
        for _ in range(daily_clicks):
            # Choose IP pool (90% normal, 5% mobile, 5% other)
            ip_pool_choice = random.choices(
                ['normal', 'mobile', 'international', 'suspicious'],
                weights=[85, 10, 4, 1]
            )[0]
            ip = random.choice(ip_pools[ip_pool_choice])
            
            # Some clicks from suspicious IPs for fraud detection demo
            if random.random() < 0.001:  # 0.1% chance
                ip = random.choice(ip_pools['suspicious'])
            
            # Create click
            click_time = date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            converted = random.random() < config['conversion']
            
            Click.objects.create(
                influencer=influencer,
                campaign=random.choice(campaigns),
                ip_address=ip,
                user_agent=random.choice(user_agents),
                converted=converted,
                created_at=click_time
            )
            total_clicks += 1
            
            # If converted, create a sale
            if converted:
                sale_time = click_time + timedelta(minutes=random.randint(5, 120))
                amount = Decimal(str(random.randint(1000, 15000)))  # $10-$150
                commission = amount * (commission_rate / Decimal('100'))
                
                # Status distribution changes over time (older = more likely paid)
                if day_offset > 30:
                    status_weights = [10, 20, 70]  # Older: more paid
                elif day_offset > 7:
                    status_weights = [30, 40, 30]  # Medium: mixed
                else:
                    status_weights = [60, 30, 10]  # Recent: more pending
                
                status = random.choices(['pending', 'approved', 'paid'], weights=status_weights)[0]
                
                # Generate unique order_id using timestamp and random
                unique_id = f"{int(sale_time.timestamp())}{random.randint(1000, 9999)}"
                sale = Sale.objects.create(
                    influencer=influencer,
                    order_id=f'ORD-{influencer.referral_code}-{unique_id}',
                    amount=amount,
                    commission=commission,
                    status=status,
                    customer_email=f'customer{unique_id}@example.com',
                    created_at=sale_time,
                    updated_at=sale_time + timedelta(days=random.randint(0, 5)) if status != 'pending' else sale_time
                )
                total_sales += 1
                
                if status == 'paid':
                    total_earnings += commission
                else:
                    total_pending += commission
    
    # Update influencer totals
    influencer.total_earnings = total_earnings
    influencer.pending_amount = total_pending
    influencer.save()
    
    # Create payment history
    if total_earnings > 0:
        num_payments = random.randint(2, 5)
        payment_amount = total_earnings / num_payments
        
        for p in range(num_payments):
            payment_date = today - timedelta(days=random.randint(1, 90))
            Payment.objects.create(
                influencer=influencer,
                amount=payment_amount,
                status=random.choice(['completed', 'completed', 'completed', 'processing']),
                payment_method=random.choice(['bank_transfer', 'paypal', 'stripe']),
                transaction_id=f'TXN-{random.randint(100000, 999999)}',
                notes=f'Payment batch #{p+1}',
                created_at=payment_date,
                completed_at=payment_date + timedelta(days=2) if random.random() > 0.3 else None
            )
    
    conversion_rate = (total_sales / total_clicks * 100) if total_clicks > 0 else 0
    print(f"   ✓ {i}. {config['username']}: {total_clicks} clicks, {total_sales} sales, "
          f"{conversion_rate:.1f}% conv, ${total_earnings} earned")

# 3. Create Admin User
print("\n3. Creating Admin User...")
try:
    admin_user, created = User.objects.update_or_create(
        username='admin',
        defaults={
            'email': 'admin@sherlock.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("   ✓ Admin: admin@sherlock.com / admin123")
    else:
        print("   ✓ Admin updated (already exists)")
except Exception as e:
    print(f"   ✓ Admin user exists (skipped)")

# 4. Create Finance User
print("\n4. Creating Finance User...")
try:
    finance_user, created = User.objects.update_or_create(
        username='finance',
        defaults={
            'email': 'finance@sherlock.com',
            'role': 'finance'
        }
    )
    if created:
        finance_user.set_password('finance123')
        finance_user.save()
        print("   ✓ Finance: finance@sherlock.com / finance123")
    else:
        print("   ✓ Finance updated (already exists)")
except Exception as e:
    print(f"   ✓ Finance user exists (skipped)")

# Summary
print("\n" + "="*60)
print("Demo Data Created Successfully!")
print("="*60)
print(f"\n📊 Statistics:")
print(f"   • Campaigns: {Campaign.objects.count()}")
print(f"   • Influencers: {Influencer.objects.count()}")
print(f"   • Total Clicks: {Click.objects.count():,}")
print(f"   • Total Sales: {Sale.objects.count():,}")
print(f"   • Total Payments: {Payment.objects.count()}")
print(f"   • Bank Accounts: {BankAccount.objects.count()}")

print(f"\n💰 Financial Summary:")
total_revenue = Sale.objects.filter(status__in=['approved', 'paid']).aggregate(
    Sum('amount'))['amount__sum'] or Decimal('0')
total_commissions = Sale.objects.filter(status__in=['approved', 'paid']).aggregate(
    Sum('commission'))['commission__sum'] or Decimal('0')
total_paid = Payment.objects.filter(status='completed').aggregate(
    Sum('amount'))['amount__sum'] or Decimal('0')

print(f"   • Total Revenue: ${total_revenue:,.2f}")
print(f"   • Total Commissions: ${total_commissions:,.2f}")
print(f"   • Total Paid Out: ${total_paid:,.2f}")

print(f"\n🎯 AI Analytics Ready:")
print(f"   • Sales Prediction: {Sale.objects.count()} sales over 120 days")
print(f"   • Fraud Detection: {Click.objects.filter(ip_address__in=ip_pools['suspicious']).count()} suspicious clicks")
print(f"   • Performance Insights: {Influencer.objects.count()} influencer profiles")

print(f"\n🔐 Login Credentials:")
print(f"   • Admin: admin@sherlock.com / admin123")
print(f"   • Finance: finance@sherlock.com / finance123")
print(f"   • Influencers: [name]@demo.com / demo123")
print(f"\n   (e.g., alice@demo.com, bob@demo.com, etc.)")

print("\n" + "="*60)
print("Next steps:")
print("   1. Start server: python manage.py runserver")
print("   2. Visit: http://localhost:8000/admin/")
print("   3. Test AI Analytics: http://localhost:8000/api/analytics/predictions/")
print("="*60)
