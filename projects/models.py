from django.db import models
from django.conf import settings
from tinymce.models import HTMLField


class Client(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Prospect', 'Prospect'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Prospect')
    notes = HTMLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='client_status_idx'),
            models.Index(fields=['email'], name='client_email_idx'),
        ]

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('Internal', 'Internal'),
        ('Client', 'Client'),
    ]

    title = models.CharField(max_length=200)
    description = HTMLField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='Internal')
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planning')
    additional_info = HTMLField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Most common queries: filter by status, sort by date; or filter by creator+status
            models.Index(fields=['status', 'created_at'], name='project_status_created_idx'),
            models.Index(fields=['created_by', 'status'], name='project_created_by_status_idx'),
        ]

    def __str__(self):
        return self.title


class Agenda(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='agendas')
    title = models.CharField(max_length=200)
    description = HTMLField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_agendas',
    )
    deadline = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-priority']
        indexes = [
            # project-scoped agenda lists filtered by status (most common list view)
            models.Index(fields=['project', 'status'], name='agenda_project_status_idx'),
            # assigned-to user dashboard: tasks assigned to me, sorted by deadline
            models.Index(fields=['assigned_to', 'deadline'], name='agenda_assigned_deadline_idx'),
        ]

    def __str__(self):
        return self.title
