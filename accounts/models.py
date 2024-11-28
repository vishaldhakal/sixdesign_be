from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    # Add any additional fields you need
    role = models.CharField(max_length=20, default='user')
    
    class Meta:
        ordering = ['-date_joined']
