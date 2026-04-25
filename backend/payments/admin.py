from django.contrib import admin
from .models import Payment, BankAccount

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'influencer', 'amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['influencer__user__email', 'transaction_id']

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['influencer', 'bank_name', 'is_verified']
