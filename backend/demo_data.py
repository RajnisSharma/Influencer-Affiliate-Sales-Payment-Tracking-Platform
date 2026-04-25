#!/usr/bin/env python
"""Create demo data for testing the Influencer Platform"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Influencer, Sale, Click, Campaign
from payments.models import Payment
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()

print("Creating demo data...")

# 1. Create Campaign
campaign, _ = Campaign.objects.get_or_create(
    name="Summer Sale 2024",
    defaults={
        'product_url': 'https://example.com/summer-sale',
        'commission_rate': Decimal('15.00'),
        'is_active': True
    }
)
print(f"✓ Campaign: {campaign.name}")

# 2. Create 5 Influencers with Sales Data
influencers_data = [
    {'email': 'alice@demo.com', 'username': 'alice_style', 'bio': 'Fashion & Lifestyle', 'social': '@alice_style'},
    {'email': 'bob@demo.com', 'username': 'bob_tech', 'bio': 'Tech Reviews', 'social': '@bobtech'},
    {'email': 'carol@demo.com', 'username': 'carol_fit', 'bio': 'Fitness & Health', 'social': '@carolfit'},
    {'email': 'dave@demo.com', 'username': 'dave_food', 'bio': 'Food & Cooking', 'social': '@davecooks'},
    {'email': 'eve@demo.com', 'username': 'eve_travel', 'bio': 'Travel Blogger', 'social': '@evetravels'},
]

for i, data in enumerate(influencers_data, 1):
    # Create user
    user, created = User.objects.get_or_create(
        email=data['email'],
        defaults={
            'username': data['username'],
            'role': 'influencer'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
    
    # Create influencer profile
    influencer, inf_created = Influencer.objects.get_or_create(
        user=user,
        defaults={
            'commission_rate': Decimal(str(random.randint(10, 20))),
            'bio': data['bio'],
            'social_handle': data['social'],
            'is_active': True
        }
    )
    
    # Generate Clicks (30-100 clicks per influencer)
    click_count = random.randint(30, 100)
    for _ in range(click_count):
        Click.objects.create(
            influencer=influencer,
            campaign=campaign,
            ip_address=f'192.168.1.{random.randint(1, 255)}',
            user_agent='Mozilla/5.0 Demo Browser',
            converted=random.random() > 0.7,  # 30% conversion rate
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
    
    # Generate Sales (5-15 sales per influencer)
    sale_count = random.randint(5, 15)
    total_earnings = Decimal('0')
    pending_amount = Decimal('0')
    
    for j in range(sale_count):
        amount = Decimal(str(random.randint(500, 5000)))
        commission = amount * (influencer.commission_rate / Decimal('100'))
        
        # Random status with weighted probability
        status = random.choices(
            ['pending', 'approved', 'paid'],
            weights=[30, 20, 50]
        )[0]
        
        sale = Sale.objects.create(
            influencer=influencer,
            order_id=f'ORD-{influencer.referral_code}-{j+1:03d}',
            amount=amount,
            commission=commission,
            status=status,
            customer_email=f'customer{j}@example.com',
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        if status == 'paid':
            total_earnings += commission
        else:
            pending_amount += commission
    
    influencer.total_earnings = total_earnings
    influencer.pending_amount = pending_amount
    influencer.save()
    
    # Create 1-2 payments for paid sales
    if total_earnings > 0:
        payment_count = random.randint(1, 2)
        for _ in range(payment_count):
            Payment.objects.create(
                influencer=influencer,
                amount=total_earnings / payment_count,
                status='completed',
                payment_method='bank_transfer',
                transaction_id=f'TXN-{random.randint(10000, 99999)}',
                created_at=datetime.now() - timedelta(days=random.randint(1, 15)),
                completed_at=datetime.now() - timedelta(days=random.randint(0, 10))
            )
    
    print(f"✓ Influencer {i}: {data['username']} - {click_count} clicks, {sale_count} sales, ${total_earnings} earned")

print("\n" + "="*50)
print("Demo data created successfully!")
print("="*50)
print(f"\nTotal Influencers: {Influencer.objects.count()}")
print(f"Total Clicks: {Click.objects.count()}")
print(f"Total Sales: {Sale.objects.count()}")
print(f"Total Payments: {Payment.objects.count()}")

print("\nDemo Credentials for all influencers:")
print("  Email: alice@demo.com / bob@demo.com / carol@demo.com / dave@demo.com / eve@demo.com")
print("  Password: demo123")
