# Generated by Django 4.0.2 on 2022-08-28 16:03

import SupportTicket.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('content', models.TextField(verbose_name='content')),
                ('image', models.ImageField(blank=True, max_length=1024, null=True, upload_to=SupportTicket.models.user_ticket_image_upload_file_path, verbose_name='Image')),
                ('ticket_id', models.CharField(blank=True, max_length=255, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'pending'), ('closed', 'closed')], default='pending', max_length=155, verbose_name='status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name_plural': 'tickets',
                'ordering': ['-created'],
            },
        ),
    ]
