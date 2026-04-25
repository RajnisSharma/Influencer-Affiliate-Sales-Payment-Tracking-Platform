import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('influencer', 'Influencer'),
        ('finance', 'Finance'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='influencer')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.role})"

class Campaign(models.Model):
    name = models.CharField(max_length=200)
    product_url = models.URLField()
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Influencer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='influencer_profile')
    referral_code = models.CharField(max_length=20, unique=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    bio = models.TextField(blank=True)
    social_handle = models.CharField(max_length=100, blank=True)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = f"INF{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.referral_code}"

class Click(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='clicks')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True)
    converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['influencer', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='sales')
    click = models.OneToOneField(Click, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['influencer', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.commission:
            rate = self.influencer.commission_rate / 100
            self.commission = self.amount * rate
        super().save(*args, **kwargs)
