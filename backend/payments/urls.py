from django.urls import path
from .views import (
    PaymentListView, PaymentDetailView, ExportReportView,
    BankAccountView, PayoutSummaryView
)

urlpatterns = [
    path('', PaymentListView.as_view()),
    path('<int:pk>/', PaymentDetailView.as_view()),
    path('export/<str:format_type>/', ExportReportView.as_view()),
    path('bank-account/', BankAccountView.as_view()),
    path('summary/', PayoutSummaryView.as_view()),
]
