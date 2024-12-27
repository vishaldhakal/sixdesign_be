from django.db import models
from django.conf import settings
from django.utils import timezone
from tinymce.models import HTMLField

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class ExpenseAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]

    expense_id = models.IntegerField()  # Store expense ID separately
    expense_title = models.CharField(max_length=200)  # Store expense title separately
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_audit_logs'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.action} expense {self.expense_title} at {self.timestamp}"

class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses'
    )
    description = HTMLField(blank=True, null=True)
    receipt = models.FileField(
        blank=True,
        null=True
    )
    receipt2 = models.FileField(
        blank=True,
        null=True
    )
    receipt3 = models.FileField(
        blank=True,
        null=True
    )
    receipt4 = models.FileField(
        blank=True,
        null=True
    )
    hst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expense_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"

    def log_action(self, user, action, changes=None, ip_address=None):
        """
        Log an action performed on this expense
        """
        return ExpenseAuditLog.objects.create(
            expense_id=self.id,
            expense_title=self.title,
            user=user,
            action=action,
            changes=changes,
            ip_address=ip_address
        )

    def save(self, *args, **kwargs):
        # Track if this is a new instance
        is_new = self._state.adding
        
        # If updating, get original state
        if not is_new:
            try:
                old_instance = Expense.objects.get(pk=self.pk)
                old_data = {
                    'title': old_instance.title,
                    'amount': str(old_instance.amount),
                    'category': old_instance.category_id,
                    'description': old_instance.description,
                    'expense_date': str(old_instance.expense_date),
                }
            except Expense.DoesNotExist:
                old_data = {}
        
        # Save the instance
        super().save(*args, **kwargs)
        
        # Get current data
        current_data = {
            'title': self.title,
            'amount': str(self.amount),
            'category': self.category_id,
            'description': self.description,
            'expense_date': str(self.expense_date),
        }
        
        # If this is a new instance, log creation
        if is_new and hasattr(self, 'created_by'):
            self.log_action(
                user=self.created_by,
                action='CREATE',
                changes=None
            )
        # If this is an update, log changes
        elif not is_new and hasattr(self, 'created_by'):
            changes = {
                field: {'old': old_data[field], 'new': current_data[field]}
                for field in current_data
                if field in old_data and old_data[field] != current_data[field]
            }
            if changes:  # Only log if there were actual changes
                self.log_action(
                    user=self.created_by,
                    action='UPDATE',
                    changes=changes
                )
