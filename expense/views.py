from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Max, Min
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer
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
        return Expense.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
