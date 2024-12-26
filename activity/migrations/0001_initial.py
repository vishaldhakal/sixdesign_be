# Generated by Django 5.1.3 on 2024-12-20 16:19

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='People',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('last_activity', models.DateTimeField(blank=True, null=True)),
                ('stage', models.CharField(blank=True, choices=[('Contact', 'Contact'), ('Buyer', 'Buyer'), ('Lead', 'Lead'), ('Nurture', 'Nurture'), ('Closed', 'Closed'), ('Past Client', 'Past Client'), ('Sphere', 'Sphere'), ('Trash', 'Trash')], max_length=100, null=True)),
                ('source', models.CharField(blank=True, max_length=100, null=True)),
                ('source_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visitor_id', models.CharField(blank=True, max_length=255, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=10, null=True)),
                ('screen_resolution', models.CharField(blank=True, max_length=50, null=True)),
                ('timezone', models.CharField(blank=True, max_length=100, null=True)),
                ('tags', models.ManyToManyField(blank=True, to='activity.tag')),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('site_id', models.CharField(default=uuid.uuid4, max_length=100, unique=True)),
                ('tracking_code', models.TextField(blank=True, null=True)),
                ('domain', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('Viewed Page', 'Viewed Page'), ('Form Submission', 'Form Submission'), ('Heartbeat', 'Heartbeat'), ('Inquiry', 'Inquiry')], max_length=100)),
                ('message', models.TextField(blank=True, null=True)),
                ('page_title', models.CharField(blank=True, max_length=255, null=True)),
                ('page_url', models.URLField(blank=True, null=True)),
                ('page_referrer', models.URLField(blank=True, max_length=2000, null=True)),
                ('page_duration', models.IntegerField(blank=True, null=True)),
                ('form_data', models.JSONField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('occured_at', models.DateTimeField(auto_now_add=True)),
                ('visitor_id', models.CharField(blank=True, max_length=255, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=10, null=True)),
                ('screen_resolution', models.CharField(blank=True, max_length=50, null=True)),
                ('timezone', models.CharField(blank=True, max_length=100, null=True)),
                ('last_heartbeat', models.DateTimeField(auto_now=True)),
                ('people', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.people')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.website')),
            ],
            options={
                'ordering': ['-occured_at'],
            },
        ),
        migrations.AddIndex(
            model_name='people',
            index=models.Index(fields=['visitor_id'], name='activity_pe_visitor_3a5507_idx'),
        ),
        migrations.AddIndex(
            model_name='people',
            index=models.Index(fields=['email'], name='activity_pe_email_a8afde_idx'),
        ),
        migrations.AddIndex(
            model_name='activity',
            index=models.Index(fields=['visitor_id'], name='activity_ac_visitor_a237b6_idx'),
        ),
        migrations.AddIndex(
            model_name='activity',
            index=models.Index(fields=['occured_at'], name='activity_ac_occured_c65755_idx'),
        ),
    ]