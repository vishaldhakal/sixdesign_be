from rest_framework import serializers
from .models import Expense, ExpenseCategory, ExpenseAuditLog
from accounts.serializers import UserSerializer
from django.utils import timezone
from decimal import Decimal

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class ExpenseAuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ExpenseAuditLog
        fields = [
            'id', 'expense_id', 'expense_title', 'action', 
            'action_display', 'changes', 'timestamp', 'ip_address'
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['changes']:
            formatted_changes = []
            for field, change in data['changes'].items():
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    formatted_changes.append({
                        'field': field,
                        'old_value': change['old'],
                        'new_value': change['new']
                    })
                else:
                    formatted_changes.append({
                        'field': field,
                        'value': change
                    })
            data['changes'] = formatted_changes
        return data

class ExpenseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    category_details = ExpenseCategorySerializer(source='category', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    audit_logs = ExpenseAuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'category', 'category_details', 
                 'description', 'receipt', 'receipt2', 'receipt3', 'receipt4', 
                 'expense_date', 'created_by', 'created_at', 'updated_at', 'audit_logs']
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'audit_logs')

    def validate(self, data):
        if data.get('expense_date') and data['expense_date'] > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future")
        return data 