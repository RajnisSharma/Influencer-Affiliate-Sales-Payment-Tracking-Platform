import uuid
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Influencer, Sale, Click, Campaign
from .serializers import (
    UserSerializer, RegisterSerializer, InfluencerSerializer,
    InfluencerCreateSerializer, SaleSerializer, SaleCreateSerializer,
    CampaignSerializer, ClickSerializer, DashboardStatsSerializer
)

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data
        if request.user.role == 'influencer':
            try:
                influencer = request.user.influencer_profile
                data['influencer'] = InfluencerSerializer(influencer).data
            except:
                pass
        return Response(data)

class InfluencerListView(APIView):
    def get(self, request):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        influencers = Influencer.objects.filter(is_active=True)
        serializer = InfluencerSerializer(influencers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)
        
        serializer = InfluencerCreateSerializer(data=request.data)
        if serializer.is_valid():
            influencer = serializer.save()
            return Response(InfluencerSerializer(influencer).data, status=201)
        return Response(serializer.errors, status=400)

class InfluencerDetailView(APIView):
    def get(self, request, pk):
        if request.user.role not in ['admin', 'finance'] and (
            not hasattr(request.user, 'influencer_profile') or 
            request.user.influencer_profile.id != int(pk)
        ):
            return Response({'error': 'Unauthorized'}, status=403)
        
        try:
            influencer = Influencer.objects.get(pk=pk)
            serializer = InfluencerSerializer(influencer)
            return Response(serializer.data)
        except Influencer.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

class TrackClickView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, referral_code):
        try:
            influencer = Influencer.objects.get(referral_code=referral_code, is_active=True)
            
            # Check for suspicious activity (same IP, many clicks)
            ip = get_client_ip(request)
            recent_clicks = Click.objects.filter(
                ip_address=ip,
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            if recent_clicks > 50:  # Suspicious
                return Response({'error': 'Suspicious activity detected'}, status=429)
            
            click = Click.objects.create(
                influencer=influencer,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
            
            # Return redirect URL (in real app, this would be the product URL)
            return Response({
                'success': True,
                'redirect_url': 'https://example.com/product',
                'click_id': click.id
            })
        except Influencer.DoesNotExist:
            return Response({'error': 'Invalid referral code'}, status=404)

class SaleListView(APIView):
    def get(self, request):
        if request.user.role == 'influencer':
            try:
                influencer = request.user.influencer_profile
                sales = Sale.objects.filter(influencer=influencer)
            except:
                return Response([])
        else:
            sales = Sale.objects.all()
        
        status_filter = request.query_params.get('status')
        if status_filter:
            sales = sales.filter(status=status_filter)
        
        serializer = SaleSerializer(sales.order_by('-created_at'), many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # This would typically be called by a webhook from your e-commerce system
        if request.user.role != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)
        
        referral_code = request.data.get('referral_code')
        try:
            influencer = Influencer.objects.get(referral_code=referral_code)
        except Influencer.DoesNotExist:
            return Response({'error': 'Invalid referral code'}, status=400)
        
        data = request.data.copy()
        data['influencer'] = influencer.id
        data['commission'] = float(data['amount']) * (influencer.commission_rate / 100)
        
        serializer = SaleSerializer(data=data)
        if serializer.is_valid():
            sale = serializer.save()
            
            # Update influencer pending amount
            influencer.pending_amount += sale.commission
            influencer.save()
            
            return Response(SaleSerializer(sale).data, status=201)
        return Response(serializer.errors, status=400)

class SaleDetailView(APIView):
    def patch(self, request, pk):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        try:
            sale = Sale.objects.get(pk=pk)
            new_status = request.data.get('status')
            
            if new_status and new_status != sale.status:
                old_status = sale.status
                sale.status = new_status
                sale.save()
                
                # Update influencer earnings
                influencer = sale.influencer
                if old_status != 'paid' and new_status == 'paid':
                    influencer.total_earnings += sale.commission
                    influencer.pending_amount -= sale.commission
                    influencer.save()
                elif old_status == 'paid' and new_status != 'paid':
                    influencer.total_earnings -= sale.commission
                    influencer.pending_amount += sale.commission
                    influencer.save()
            
            return Response(SaleSerializer(sale).data)
        except Sale.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

class DashboardStatsView(APIView):
    def get(self, request):
        is_influencer = request.user.role == 'influencer'
        
        if is_influencer:
            try:
                influencer = request.user.influencer_profile
                sales = Sale.objects.filter(influencer=influencer)
                clicks = Click.objects.filter(influencer=influencer)
            except:
                return Response({
                    'total_sales': 0,
                    'total_commissions': 0,
                    'total_clicks': 0,
                    'conversion_rate': 0,
                    'pending_payments': 0
                })
        else:
            sales = Sale.objects.all()
            clicks = Click.objects.all()
        
        # Calculate stats
        total_sales = sales.filter(status__in=['approved', 'paid']).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_commissions = sales.filter(status='paid').aggregate(
            total=Sum('commission')
        )['total'] or 0
        
        total_clicks = clicks.count()
        converted_clicks = clicks.filter(converted=True).count()
        conversion_rate = (converted_clicks / total_clicks * 100) if total_clicks > 0 else 0
        
        pending_payments = sales.filter(status='pending').aggregate(
            total=Sum('commission')
        )['total'] or 0
        
        active_influencers = Influencer.objects.filter(is_active=True).count() if not is_influencer else 0
        
        return Response({
            'total_sales': total_sales,
            'total_commissions': total_commissions,
            'total_clicks': total_clicks,
            'conversion_rate': round(conversion_rate, 2),
            'pending_payments': pending_payments,
            'active_influencers': active_influencers
        })

class CampaignListView(APIView):
    def get(self, request):
        campaigns = Campaign.objects.filter(is_active=True)
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Unauthorized'}, status=403)
        
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
