from rest_framework import serializers
from .models import Expense, ExpenseCategory, ExpenseAuditLog
from django.utils import timezone


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ('id', 'name', 'description')


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class ExpenseAuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ExpenseAuditLog
        fields = ('id', 'expense_id', 'expense_title', 'action', 'action_display',
                  'changes', 'timestamp', 'ip_address')
        read_only_fields = ('id', 'expense_id', 'expense_title', 'action',
                            'action_display', 'changes', 'timestamp', 'ip_address')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['changes']:
            formatted = []
            for field, change in data['changes'].items():
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    formatted.append({'field': field, 'old_value': change['old'], 'new_value': change['new']})
                else:
                    formatted.append({'field': field, 'value': change})
            data['changes'] = formatted
        return data


# ---------------------------------------------------------------------------
# Expense — list vs detail
# ---------------------------------------------------------------------------

class ExpenseListSerializer(serializers.ModelSerializer):
    """
    Lightweight list: only the fields a table/card row needs.
    No nested audit logs, no full UserSerializer — just category name.
    Views feed this with .values() when possible, or .only() + select_related.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = ('id', 'title', 'amount', 'category', 'category_name',
                  'expense_date', 'created_at')
        read_only_fields = ('created_at',)


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """
    Full expense: includes receipts, description, audit log, creator details.
    Used only on retrieve / create / update.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    audit_logs = ExpenseAuditLogSerializer(
        source='expenseauditlog_set', many=True, read_only=True
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Expense
        fields = ('id', 'title', 'amount', 'hst',
                  'category', 'category_name',
                  'description', 'expense_date',
                  'receipt', 'receipt2', 'receipt3', 'receipt4',
                  'created_by', 'created_by_name',
                  'created_at', 'updated_at',
                  'audit_logs')
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'audit_logs')

    def get_created_by_name(self, obj):
        u = obj.created_by
        return f"{u.first_name} {u.last_name}".strip() or u.username

    def validate(self, data):
        if data.get('expense_date') and data['expense_date'] > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return data