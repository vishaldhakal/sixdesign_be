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
