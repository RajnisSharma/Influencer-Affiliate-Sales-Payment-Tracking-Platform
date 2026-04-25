from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Influencer, Sale, Click, Campaign

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ['user', 'referral_code', 'commission_rate', 'total_earnings', 'is_active']
    search_fields = ['user__email', 'referral_code']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['influencer', 'amount', 'commission', 'status', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ['influencer', 'ip_address', 'user_agent', 'converted', 'created_at']
    list_filter = ['converted', 'created_at']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_url', 'commission_rate', 'is_active', 'start_date']
