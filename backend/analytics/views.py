import os
import json
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from groq import Groq
import numpy as np
from sklearn.linear_model import LinearRegression

from core.models import Influencer, Sale, Click

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY', 'GROQ_API_KEY'))

class SalesPredictionView(APIView):
    """AI-powered sales prediction using historical data"""
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        
        # Get historical sales data (last 90 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)
        
        sales = Sale.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            status__in=['approved', 'paid']
        ).values('created_at__date').annotate(
            daily_sales=Sum('amount'),
            daily_count=Count('id')
        ).order_by('created_at__date')
        
        if len(sales) < 7:
            return Response({
                'predictions': [],
                'message': 'Insufficient data for prediction (need at least 7 days)',
                'confidence': 0
            })
        
        # Prepare data for ML model
        dates = []
        amounts = []
        counts = []
        
        for i, sale in enumerate(sales):
            dates.append(i)
            amounts.append(float(sale['daily_sales'] or 0))
            counts.append(sale['daily_count'])
        
        # Linear regression for trend
        X = np.array(dates).reshape(-1, 1)
        y_amounts = np.array(amounts)
        y_counts = np.array(counts)
        
        model_amount = LinearRegression()
        model_count = LinearRegression()
        
        model_amount.fit(X, y_amounts)
        model_count.fit(X, y_counts)
        
        # Predict next N days
        future_dates = np.array(range(len(dates), len(dates) + days)).reshape(-1, 1)
        predicted_amounts = model_amount.predict(future_dates)
        predicted_counts = model_count.predict(future_dates)
        
        # Ensure non-negative predictions
        predicted_amounts = np.maximum(predicted_amounts, 0)
        predicted_counts = np.maximum(predicted_counts, 0)
        
        predictions = []
        for i in range(days):
            date = end_date + timedelta(days=i+1)
            predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_revenue': round(predicted_amounts[i], 2),
                'predicted_sales': round(predicted_counts[i])
            })
        
        # Calculate confidence (R-squared score)
        confidence = model_amount.score(X, y_amounts)
        
        # Generate AI insight using Groq
        insight = self._generate_prediction_insight(sales, predictions, confidence)
        
        return Response({
            'predictions': predictions,
            'confidence': round(confidence * 100, 1),
            'total_predicted_revenue': round(sum(predicted_amounts), 2),
            'total_predicted_sales': round(sum(predicted_counts)),
            'ai_insight': insight
        })
    
    def _generate_prediction_insight(self, historical, predictions, confidence):
        if not groq_client.api_key:
            return "AI insights unavailable. Configure GROQ_API_KEY for AI-powered analysis."
        
        try:
            recent_avg = sum(float(s['daily_sales'] or 0) for s in historical[-7:]) / 7
            predicted_avg = sum(p['predicted_revenue'] for p in predictions[:7]) / 7
            trend = "increasing" if predicted_avg > recent_avg else "decreasing"
            
            prompt = f"""
            Based on sales data:
            - Recent 7-day average revenue: ${recent_avg:.2f}
            - Predicted 7-day average: ${predicted_avg:.2f}
            - Trend: {trend}
            - Model confidence: {confidence*100:.1f}%
            
            Provide a brief 1-2 sentence business insight about this sales prediction.
            """
            
            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Based on current trends, sales are expected to {trend} with {confidence*100:.1f}% confidence."


class InfluencerInsightsView(APIView):
    """AI-powered influencer performance insights"""
    
    def get(self, request):
        influencer_id = request.query_params.get('influencer_id')
        
        if influencer_id:
            try:
                influencer = Influencer.objects.get(id=influencer_id)
                insights = self._analyze_influencer(influencer)
            except Influencer.DoesNotExist:
                return Response({'error': 'Influencer not found'}, status=404)
        else:
            if request.user.role == 'influencer':
                try:
                    influencer = request.user.influencer_profile
                    insights = self._analyze_influencer(influencer)
                except:
                    return Response({'error': 'No influencer profile found'}, status=404)
            else:
                # Analyze all influencers for admin
                influencers = Influencer.objects.filter(is_active=True)[:10]
                insights = []
                for inf in influencers:
                    inf_insight = self._analyze_influencer(inf)
                    insights.append({
                        'influencer': inf.user.email,
                        'referral_code': inf.referral_code,
                        **inf_insight
                    })
        
        return Response({'insights': insights})
    
    def _analyze_influencer(self, influencer):
        # Get last 60 days of data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=60)
        
        sales = Sale.objects.filter(
            influencer=influencer,
            created_at__gte=start_date,
            status__in=['approved', 'paid']
        )
        
        clicks = Click.objects.filter(
            influencer=influencer,
            created_at__gte=start_date
        )
        
        total_sales = sales.count()
        total_revenue = sales.aggregate(Sum('amount'))['amount__sum'] or 0
        total_clicks = clicks.count()
        converted_clicks = clicks.filter(converted=True).count()
        
        conversion_rate = (converted_clicks / total_clicks * 100) if total_clicks > 0 else 0
        
        # Day of week analysis
        day_performance = {}
        for sale in sales:
            day = sale.created_at.strftime('%A')
            day_performance[day] = day_performance.get(day, 0) + float(sale.amount)
        
        best_day = max(day_performance, key=day_performance.get) if day_performance else None
        
        # Calculate metrics
        avg_order_value = float(total_revenue) / total_sales if total_sales > 0 else 0
        
        # Generate insights
        insights = {
            'total_sales': total_sales,
            'total_revenue': round(float(total_revenue), 2),
            'total_clicks': total_clicks,
            'conversion_rate': round(conversion_rate, 2),
            'avg_order_value': round(avg_order_value, 2),
            'best_performing_day': best_day,
            'performance_score': self._calculate_score(conversion_rate, total_sales, avg_order_value),
            'recommendations': self._generate_recommendations(
                conversion_rate, total_clicks, best_day, influencer
            )
        }
        
        return insights
    
    def _calculate_score(self, conversion_rate, total_sales, avg_order_value):
        # Simple scoring algorithm (0-100)
        score = min(conversion_rate * 5, 40)  # Up to 40 points for conversion
        score += min(total_sales * 2, 30)      # Up to 30 points for volume
        score += min(avg_order_value / 10, 30)  # Up to 30 points for value
        return round(score)
    
    def _generate_recommendations(self, conversion_rate, total_clicks, best_day, influencer):
        recommendations = []
        
        if conversion_rate < 2:
            recommendations.append("Low conversion rate. Consider reviewing your audience targeting or product messaging.")
        
        if total_clicks > 100 and conversion_rate < 1:
            recommendations.append("High traffic but low conversions. Your clicks may not be from qualified buyers.")
        
        if best_day:
            recommendations.append(f"Your content performs best on {best_day}s. Schedule more posts on this day.")
        
        if influencer.total_earnings > 0 and influencer.pending_amount > float(influencer.total_earnings) * 0.5:
            recommendations.append("You have significant pending payments. Follow up on payment status.")
        
        # AI-powered insight using Groq
        ai_insight = self._generate_ai_insight(influencer, conversion_rate, total_clicks, best_day)
        if ai_insight:
            recommendations.append(ai_insight)
        
        return recommendations
    
    def _generate_ai_insight(self, influencer, conversion_rate, total_clicks, best_day):
        if not groq_client.api_key:
            return None
        
        try:
            prompt = f"""
            Analyze this influencer performance:
            - Referral code: {influencer.referral_code}
            - Conversion rate: {conversion_rate:.1f}%
            - Total clicks: {total_clicks}
            - Best day: {best_day}
            - Total earnings: ${influencer.total_earnings}
            
            Provide ONE actionable tip to improve performance. Keep it under 100 characters.
            """
            
            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except:
            return None


class FraudDetectionView(APIView):
    """AI-powered fraud detection for clicks and conversions"""
    
    def get(self, request):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Analyze last 24 hours for suspicious activity
        end_date = timezone.now()
        start_date = end_date - timedelta(hours=24)
        
        suspicious_activity = []
        
        # Check 1: Multiple clicks from same IP
        from django.db.models import Count as DjangoCount
        
        ip_clicks = Click.objects.filter(
            created_at__gte=start_date
        ).values('ip_address').annotate(
            click_count=DjangoCount('id')
        ).filter(click_count__gt=50)
        
        for ip_data in ip_clicks[:10]:
            suspicious_activity.append({
                'type': 'suspicious_ip',
                'ip_address': ip_data['ip_address'],
                'click_count': ip_data['click_count'],
                'risk_level': 'high' if ip_data['click_count'] > 100 else 'medium',
                'message': f"IP {ip_data['ip_address']} made {ip_data['click_count']} clicks in 24h"
            })
        
        # Check 2: Influencers with abnormally high conversion rates
        influencers = Influencer.objects.filter(is_active=True)
        for influencer in influencers:
            clicks = Click.objects.filter(influencer=influencer, created_at__gte=start_date-timedelta(days=7))
            total_clicks = clicks.count()
            converted = clicks.filter(converted=True).count()
            
            if total_clicks > 20:
                rate = (converted / total_clicks) * 100
                if rate > 80:  # Suspiciously high conversion rate
                    suspicious_activity.append({
                        'type': 'suspicious_conversion',
                        'influencer': influencer.user.email,
                        'conversion_rate': round(rate, 1),
                        'risk_level': 'high',
                        'message': f"{influencer.user.email} has {rate:.1f}% conversion rate (suspicious)"
                    })
        
        # Check 3: Rapid-fire clicks (bot-like behavior)
        # This would require more complex query in production
        
        return Response({
            'suspicious_count': len(suspicious_activity),
            'activities': suspicious_activity,
            'review_recommended': len(suspicious_activity) > 0
        })


class TopInfluencersView(APIView):
    """Get top performing influencers"""
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        influencers = Influencer.objects.filter(
            is_active=True,
            sales__created_at__gte=start_date,
            sales__status__in=['approved', 'paid']
        ).annotate(
            total_revenue=Sum('sales__amount'),
            total_sales=Count('sales'),
            avg_commission=Avg('sales__commission')
        ).order_by('-total_revenue')[:10]
        
        result = []
        for inf in influencers:
            clicks = Click.objects.filter(
                influencer=inf,
                created_at__gte=start_date
            ).count()
            
            result.append({
                'id': inf.id,
                'name': inf.user.email,
                'referral_code': inf.referral_code,
                'revenue': float(inf.total_revenue or 0),
                'sales_count': inf.total_sales,
                'clicks': clicks,
                'conversion_rate': round((inf.total_sales / clicks * 100), 2) if clicks > 0 else 0,
                'commission_earned': float(inf.total_earnings)
            })
        
        return Response(result)
