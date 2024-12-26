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
        ('VIEW', 'Viewed'),
    ]

    expense = models.ForeignKey(
        'Expense',
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
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
        return f"{self.user} {self.action} expense {self.expense} at {self.timestamp}"

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
            expense=self,
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
            old_instance = Expense.objects.get(pk=self.pk)
            
        super().save(*args, **kwargs)
