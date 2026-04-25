from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Influencer, Sale, Click, Campaign

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'role']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if user.role == 'influencer':
            Influencer.objects.create(user=user)
        return user

class InfluencerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Influencer
        fields = ['id', 'user', 'referral_code', 'commission_rate', 'total_earnings', 
                  'pending_amount', 'bio', 'social_handle', 'is_active', 'created_at']

class InfluencerCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = Influencer
        fields = ['email', 'password', 'username', 'commission_rate', 'bio', 'social_handle']
    
    def create(self, validated_data):
        user_data = {
            'email': validated_data.pop('email'),
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'role': 'influencer'
        }
        user = User.objects.create_user(**user_data)
        return Influencer.objects.create(user=user, **validated_data)

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    influencer_name = serializers.CharField(source='influencer.user.email', read_only=True)
    referral_code = serializers.CharField(source='influencer.referral_code', read_only=True)
    
    class Meta:
        model = Sale
        fields = ['id', 'influencer', 'influencer_name', 'referral_code', 'order_id', 
                  'amount', 'commission', 'status', 'customer_email', 'created_at', 'updated_at']

class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['order_id', 'amount', 'customer_email']

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = '__all__'

class DashboardStatsSerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_commissions = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_clicks = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    active_influencers = serializers.IntegerField()
    pending_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
