from django.db import models

# Create your models here.

class UnsubscribeEmails(models.Model):
    email = models.EmailField(unique=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Unsubscribe Email'
        verbose_name_plural = 'Unsubscribe Emails'
