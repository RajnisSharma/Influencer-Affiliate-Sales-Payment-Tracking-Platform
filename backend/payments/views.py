import csv
import io
from datetime import datetime, timedelta
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from core.models import Influencer, Sale
from .models import Payment, BankAccount

class PaymentListView(APIView):
    def get(self, request):
        if request.user.role == 'influencer':
            try:
                influencer = request.user.influencer_profile
                payments = Payment.objects.filter(influencer=influencer)
            except:
                return Response([])
        else:
            payments = Payment.objects.all()
        
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        result = []
        for payment in payments.order_by('-created_at'):
            result.append({
                'id': payment.id,
                'influencer': payment.influencer.user.email,
                'referral_code': payment.influencer.referral_code,
                'amount': float(payment.amount),
                'status': payment.status,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at,
                'completed_at': payment.completed_at
            })
        
        return Response(result)
    
    def post(self, request):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        influencer_id = request.data.get('influencer_id')
        try:
            influencer = Influencer.objects.get(id=influencer_id)
        except Influencer.DoesNotExist:
            return Response({'error': 'Influencer not found'}, status=404)
        
        # Get approved sales that haven't been paid
        approved_sales = Sale.objects.filter(
            influencer=influencer,
            status='approved'
        )
        
        total_amount = approved_sales.aggregate(Sum('commission'))['commission__sum'] or 0
        
        if total_amount <= 0:
            return Response({'error': 'No pending payments for this influencer'}, status=400)
        
        payment = Payment.objects.create(
            influencer=influencer,
            amount=total_amount,
            status='pending',
            payment_method=request.data.get('payment_method', 'bank_transfer')
        )
        
        # Link sales to this payment
        payment.sales_included.set(approved_sales)
        
        # Mark sales as paid
        approved_sales.update(status='paid')
        
        # Update influencer
        influencer.pending_amount -= total_amount
        influencer.total_earnings += total_amount
        influencer.save()
        
        return Response({
            'id': payment.id,
            'amount': float(payment.amount),
            'status': payment.status,
            'influencer': influencer.user.email,
            'sales_count': approved_sales.count()
        }, status=201)


class PaymentDetailView(APIView):
    def patch(self, request, pk):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        try:
            payment = Payment.objects.get(pk=pk)
            new_status = request.data.get('status')
            
            if new_status:
                payment.status = new_status
                if new_status == 'completed':
                    payment.completed_at = datetime.now()
                    payment.transaction_id = request.data.get('transaction_id', '')
                payment.save()
            
            return Response({
                'id': payment.id,
                'status': payment.status,
                'transaction_id': payment.transaction_id
            })
        except Payment.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class ExportReportView(APIView):
    def get(self, request, format_type):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        if format_type == 'csv':
            return self._export_csv(start_date)
        elif format_type == 'pdf':
            return self._export_pdf(start_date)
        else:
            return Response({'error': 'Invalid format. Use csv or pdf'}, status=400)
    
    def _export_csv(self, start_date):
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Influencer', 'Referral Code', 'Total Sales', 'Total Revenue',
            'Commission Earned', 'Pending Amount', 'Conversion Rate',
            'Status'
        ])
        
        # Data
        influencers = Influencer.objects.filter(is_active=True)
        for inf in influencers:
            sales = Sale.objects.filter(
                influencer=inf,
                created_at__gte=start_date
            )
            total_sales = sales.count()
            revenue = sales.aggregate(Sum('amount'))['amount__sum'] or 0
            
            from core.models import Click
            clicks = Click.objects.filter(influencer=inf, created_at__gte=start_date).count()
            conversion_rate = (total_sales / clicks * 100) if clicks > 0 else 0
            
            writer.writerow([
                inf.user.email,
                inf.referral_code,
                total_sales,
                float(revenue),
                float(inf.total_earnings),
                float(inf.pending_amount),
                f"{conversion_rate:.1f}%",
                'Active' if inf.is_active else 'Inactive'
            ])
        
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="influencer_report_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response
    
    def _export_pdf(self, start_date):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph("Influencer Performance Report", styles['Heading1']))
        elements.append(Paragraph(f"Period: {start_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Paragraph(" ", styles['Normal']))
        
        # Table data
        data = [['Influencer', 'Code', 'Sales', 'Revenue', 'Earned', 'Pending', 'Conv. Rate']]
        
        influencers = Influencer.objects.filter(is_active=True)
        for inf in influencers:
            sales = Sale.objects.filter(
                influencer=inf,
                created_at__gte=start_date
            )
            total_sales = sales.count()
            revenue = sales.aggregate(Sum('amount'))['amount__sum'] or 0
            
            from core.models import Click
            clicks = Click.objects.filter(influencer=inf, created_at__gte=start_date).count()
            conversion_rate = (total_sales / clicks * 100) if clicks > 0 else 0
            
            data.append([
                inf.user.email[:20],
                inf.referral_code,
                str(total_sales),
                f"${float(revenue):.0f}",
                f"${float(inf.total_earnings):.0f}",
                f"${float(inf.pending_amount):.0f}",
                f"{conversion_rate:.1f}%"
            ])
        
        # Create table
        table = Table(data, colWidths=[100, 70, 50, 60, 60, 60, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="influencer_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response


class BankAccountView(APIView):
    def get(self, request):
        if request.user.role != 'influencer':
            return Response({'error': 'Unauthorized'}, status=403)
        
        try:
            account = BankAccount.objects.get(influencer=request.user.influencer_profile)
            return Response({
                'account_holder': account.account_holder,
                'bank_name': account.bank_name,
                'account_number': '****' + account.account_number[-4:],
                'ifsc_code': account.ifsc_code,
                'is_verified': account.is_verified
            })
        except BankAccount.DoesNotExist:
            return Response({'error': 'No bank account found'}, status=404)
    
    def post(self, request):
        if request.user.role != 'influencer':
            return Response({'error': 'Unauthorized'}, status=403)
        
        try:
            influencer = request.user.influencer_profile
        except:
            return Response({'error': 'No influencer profile'}, status=400)
        
        BankAccount.objects.update_or_create(
            influencer=influencer,
            defaults={
                'account_holder': request.data.get('account_holder'),
                'account_number': request.data.get('account_number'),
                'bank_name': request.data.get('bank_name'),
                'ifsc_code': request.data.get('ifsc_code'),
            }
        )
        
        return Response({'message': 'Bank account saved successfully'})


class PayoutSummaryView(APIView):
    def get(self, request):
        if request.user.role not in ['admin', 'finance']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Summary stats
        pending_payments = Sale.objects.filter(status='pending').count()
        pending_amount = Sale.objects.filter(status='pending').aggregate(
            Sum('commission')
        )['commission__sum'] or 0
        
        approved_payments = Sale.objects.filter(status='approved').count()
        approved_amount = Sale.objects.filter(status='approved').aggregate(
            Sum('commission')
        )['commission__sum'] or 0
        
        total_paid = Payment.objects.filter(status='completed').aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        
        influencers_with_pending = Influencer.objects.filter(
            sales__status='pending'
        ).distinct().count()
        
        return Response({
            'pending_payments': {
                'count': pending_payments,
                'amount': float(pending_amount)
            },
            'approved_payments': {
                'count': approved_payments,
                'amount': float(approved_amount)
            },
            'total_paid_to_date': float(total_paid),
            'influencers_with_pending': influencers_with_pending,
            'ready_for_payout': {
                'count': approved_payments,
                'amount': float(approved_amount)
            }
        })
