from django.urls import path
from .views import (
    SalesPredictionView, InfluencerInsightsView,
    FraudDetectionView, TopInfluencersView
)

urlpatterns = [
    path('predictions/', SalesPredictionView.as_view()),
    path('insights/', InfluencerInsightsView.as_view()),
    path('fraud-detection/', FraudDetectionView.as_view()),
    path('top-influencers/', TopInfluencersView.as_view()),
]
