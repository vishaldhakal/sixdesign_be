from rest_framework import serializers
from .models import Expense, ExpenseCategory
from accounts.serializers import UserSerializer
from django.utils import timezone
from decimal import Decimal

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    category_details = ExpenseCategorySerializer(source='category', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'category', 'category_details', 
                 'description', 'receipt', 'expense_date', 'created_by', 
                 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def validate(self, data):
        if data.get('expense_date') and data['expense_date'] > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future")
        return data 