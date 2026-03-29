from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from .models import Expense, ExpenseCategory, ExpenseAuditLog
from .serializers import (
    ExpenseListSerializer, ExpenseDetailSerializer,
    ExpenseCategorySerializer, ExpenseAuditLogSerializer,
)


# ---------------------------------------------------------------------------
# Expense Category
# ---------------------------------------------------------------------------

class ExpenseCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def list(self, request, *args, **kwargs):
        # Categories are a tiny lookup table — .values() is the sweet spot
        data = list(ExpenseCategory.objects.values('id', 'name', 'description'))
        return Response(data)

    def get_queryset(self):
        return ExpenseCategory.objects.all()


class ExpenseCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


# ---------------------------------------------------------------------------
# Expense ViewSet
# ---------------------------------------------------------------------------

class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'expense_date']
    search_fields = ['title']
    ordering_fields = ['expense_date', 'amount', 'created_at']

    def get_serializer_class(self):
        # Lightweight serializer for list; full detail for everything else
        if self.action == 'list':
            return ExpenseListSerializer
        return ExpenseDetailSerializer

    def get_queryset(self):
        if self.action == 'list':
            # .only() + select_related: hits only the columns ExpenseListSerializer needs
            return (
                Expense.objects
                .filter(created_by=self.request.user)
                .select_related('category')
                .only(
                    'id', 'title', 'amount', 'expense_date', 'created_at',
                    'category__id', 'category__name',
                )
            )
        # Detail / create / update: full model + audit log prefetch
        return (
            Expense.objects
            .filter(created_by=self.request.user)
            .select_related('category', 'created_by')
            .prefetch_related('expenseauditlog_set')
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.log_action(
            user=self.request.user,
            action='DELETE',
            changes={'deleted_at': timezone.now().isoformat()},
            ip_address=self._get_client_ip(),
        )
        instance.delete()

    def _get_client_ip(self):
        xff = self.request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0] if xff else self.request.META.get('REMOTE_ADDR')

    # ------------------------------------------------------------------
    # Custom actions
    # ------------------------------------------------------------------

    @action(detail=False, methods=['get'], url_path='my-activity', url_name='my-activity')
    def my_activity(self, request):
        """
        All expense-related audit events for the current user, grouped by date.
        Uses .values() — no model overhead, just the columns the UI needs.
        """
        logs = list(
            ExpenseAuditLog.objects
            .filter(user=request.user)
            .order_by('-timestamp')
            .values('id', 'expense_id', 'expense_title', 'action', 'changes', 'timestamp', 'ip_address')
        )

        # Group by date string
        activities: dict = {}
        for log in logs:
            date_key = log['timestamp'].date().isoformat()
            activities.setdefault(date_key, []).append(log)

        return Response({'activities': activities})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Aggregated expense stats — purely DB-level maths, no model instantiation."""
        base_qs = (
            Expense.objects
            .filter(created_by=request.user)
        )
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        stats = {
            'week': base_qs.filter(expense_date__gte=week_start, expense_date__lte=today)
                           .aggregate(t=Sum('amount'))['t'] or 0,
            'month': base_qs.filter(expense_date__year=today.year, expense_date__month=today.month)
                            .aggregate(t=Sum('amount'))['t'] or 0,
            'year': base_qs.filter(expense_date__year=today.year)
                           .aggregate(t=Sum('amount'))['t'] or 0,
        }

        total = base_qs.aggregate(t=Sum('amount'))['t'] or 0

        # Category breakdown: pure aggregation
        by_category = list(
            base_qs.values('category__name').annotate(total=Sum('amount')).order_by('-total')
        )

        # Monthly trend: pure aggregation
        monthly = list(
            base_qs
            .annotate(month=TruncMonth('expense_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('-month')
        )

        # Recent 5: lightweight .values() — no model overhead
        recent = list(
            base_qs.order_by('-expense_date')
            .values('id', 'title', 'amount', 'expense_date', 'category__name')[:5]
        )

        return Response({
            'total_expenses': total,
            'stats': stats,
            'by_category': by_category,
            'monthly_expenses': monthly,
            'recent_expenses': recent,
        })
