from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Max, Min
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Expense, ExpenseCategory, ExpenseAuditLog
from .serializers import ExpenseSerializer, ExpenseCategorySerializer, ExpenseAuditLogSerializer
from django.db.models.functions import TruncMonth, TruncYear, TruncWeek, ExtractWeek, ExtractYear
from django.utils import timezone
from datetime import timedelta, datetime, date

# Create your views here.

class ExpenseCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

class ExpenseCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'expense_date']
    search_fields = ['title', 'description']
    ordering_fields = ['expense_date', 'amount', 'created_at']

    def get_queryset(self):
        return Expense.objects.filter(created_by=self.request.user)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')

    def perform_create(self, serializer):
        expense = serializer.save(created_by=self.request.user)
        expense.log_action(
            user=self.request.user,
            action='CREATE',
            ip_address=self.get_client_ip()
        )

    def perform_update(self, serializer):
        # Get the old instance data
        old_data = ExpenseSerializer(self.get_object()).data
        # Save the new instance
        expense = serializer.save()
        # Get the new instance data
        new_data = ExpenseSerializer(expense).data
        
        # Calculate changes
        changes = {
            field: {'old': old_data[field], 'new': new_data[field]}
            for field in new_data
            if field in old_data and old_data[field] != new_data[field]
        }
        
        expense.log_action(
            user=self.request.user,
            action='UPDATE',
            changes=changes,
            ip_address=self.get_client_ip()
        )

    def perform_destroy(self, instance):
        instance.log_action(
            user=self.request.user,
            action='DELETE',
            ip_address=self.get_client_ip()
        )
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.log_action(
            user=request.user,
            action='VIEW',
            ip_address=self.get_client_ip()
        )
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_activity(self, request):
        """
        Get all expense-related activities for the current user
        """
        audit_logs = ExpenseAuditLog.objects.filter(
            user=request.user
        ).select_related('expense', 'user').order_by('-timestamp')
        
        serializer = ExpenseAuditLogSerializer(audit_logs, many=True)
        
        # Group activities by date
        activities = {}
        for log in serializer.data:
            date = log['timestamp'].split('T')[0]
            if date not in activities:
                activities[date] = []
            activities[date].append(log)
        
        return Response({
            'activities': activities
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset()
        
        # Get current date (without time)
        current_date = timezone.now().date()
        
        # Calculate start dates for different periods
        week_start = current_date - timedelta(days=current_date.weekday())
        
        # Calculate expenses for different time periods
        weekly_expense = queryset.filter(
            expense_date__gte=week_start,
            expense_date__lte=current_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expense = queryset.filter(
            expense_date__year=current_date.year,
            expense_date__month=current_date.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        yearly_expense = queryset.filter(
            expense_date__year=current_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Total expenses
        total_expenses = queryset.aggregate(total=Sum('amount'))['total'] or 0

        # Expenses by category
        by_category = queryset.values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')

        # Monthly expenses for all time
        monthly_expenses = queryset.annotate(
            month=TruncMonth('expense_date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('-month')  # Order by most recent month first

        # Recent expenses
        recent_expenses = ExpenseSerializer(
            queryset.order_by('-expense_date')[:5],
            many=True
        ).data

        return Response({
            'total_expenses': total_expenses,
            'by_category': by_category,
            'stats': {
                'week': weekly_expense,
                'month': monthly_expense,
                'year': yearly_expense
            },
            'monthly_expenses': monthly_expenses,
            'recent_expenses': recent_expenses
        })
