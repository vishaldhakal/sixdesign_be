from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer
from django.db.models.functions import TruncMonth
from django.utils import timezone

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
        
        # Total expenses
        total_expenses = queryset.aggregate(total=Sum('amount'))['total'] or 0

        # Expenses by category
        by_category = queryset.values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')

        # Monthly expenses for the current year
        current_year = timezone.now().year
        monthly_expenses = queryset.filter(
            expense_date__year=current_year
        ).annotate(
            month=TruncMonth('expense_date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')

        # Recent expenses
        recent_expenses = ExpenseSerializer(
            queryset.order_by('-expense_date')[:5],
            many=True
        ).data

        return Response({
            'total_expenses': total_expenses,
            'by_category': by_category,
            'monthly_expenses': monthly_expenses,
            'recent_expenses': recent_expenses
        })
