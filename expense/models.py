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

    # Intentionally denormalised: expense may be deleted but log must survive
    expense_id = models.IntegerField()
    expense_title = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_audit_logs',
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            # look up all audit logs for a specific expense (e.g. on detail page)
            models.Index(fields=['expense_id'], name='auditlog_expense_id_idx'),
            # user activity dashboard: my actions sorted by time
            models.Index(fields=['user', 'timestamp'], name='auditlog_user_timestamp_idx'),
        ]

    def __str__(self):
        return f"{self.user} {self.action} expense '{self.expense_title}' at {self.timestamp}"


class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses',
    )
    description = HTMLField(blank=True, null=True)
    receipt = models.FileField(blank=True, null=True)
    receipt2 = models.FileField(blank=True, null=True)
    receipt3 = models.FileField(blank=True, null=True)
    receipt4 = models.FileField(blank=True, null=True)
    hst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expense_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']
        indexes = [
            # Most critical: user-scoped list filtered by date (primary list query)
            models.Index(fields=['created_by', 'expense_date'], name='expense_user_date_idx'),
            # Category filter within a user scope (used in summary breakdown)
            models.Index(fields=['created_by', 'category'], name='expense_user_category_idx'),
        ]

    def __str__(self):
        return f"{self.title} — {self.amount}"

    def log_action(self, user, action, changes=None, ip_address=None):
        """Log an action performed on this expense."""
        return ExpenseAuditLog.objects.create(
            expense_id=self.id,
            expense_title=self.title,
            user=user,
            action=action,
            changes=changes,
            ip_address=ip_address,
        )

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if not is_new:
            try:
                old = Expense.objects.only(
                    'title', 'amount', 'category_id', 'description', 'expense_date'
                ).get(pk=self.pk)
                old_data = {
                    'title': old.title,
                    'amount': str(old.amount),
                    'category': old.category_id,
                    'description': old.description,
                    'expense_date': str(old.expense_date),
                }
            except Expense.DoesNotExist:
                old_data = {}

        super().save(*args, **kwargs)

        current_data = {
            'title': self.title,
            'amount': str(self.amount),
            'category': self.category_id,
            'description': self.description,
            'expense_date': str(self.expense_date),
        }

        if is_new and hasattr(self, 'created_by'):
            self.log_action(user=self.created_by, action='CREATE')
        elif not is_new and hasattr(self, 'created_by') and old_data:
            changes = {
                field: {'old': old_data[field], 'new': current_data[field]}
                for field in current_data
                if field in old_data and old_data[field] != current_data[field]
            }
            if changes:
                self.log_action(user=self.created_by, action='UPDATE', changes=changes)
