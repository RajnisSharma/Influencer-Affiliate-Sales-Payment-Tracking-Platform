from django.urls import path
from .views import (
    RegisterView, MeView, InfluencerListView, InfluencerDetailView,
    TrackClickView, SaleListView, SaleDetailView, DashboardStatsView,
    CampaignListView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/me/', MeView.as_view()),
    
    path('influencers/', InfluencerListView.as_view()),
    path('influencers/<int:pk>/', InfluencerDetailView.as_view()),
    
    path('track/<str:referral_code>/', TrackClickView.as_view()),
    
    path('sales/', SaleListView.as_view()),
    path('sales/<int:pk>/', SaleDetailView.as_view()),
    
    path('campaigns/', CampaignListView.as_view()),
    
    path('dashboard/stats/', DashboardStatsView.as_view()),
]
