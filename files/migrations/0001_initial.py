# Generated by Django 4.2.2 on 2024-04-20 08:59

import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import files.storage_config


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.CharField(default=core.utils.generate_model_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('legacy_id', models.IntegerField(null=True)),
                ('display_id', models.CharField(editable=False, max_length=16)),
                ('file', models.FileField(storage=files.storage_config.PrivateMediaStorage(), upload_to='uploads/')),
                ('thumbnail', models.FileField(null=True, storage=files.storage_config.PrivateMediaStorage(), upload_to='uploads/')),
                ('micro_thumbnail', models.FileField(null=True, storage=files.storage_config.PrivateMediaStorage(), upload_to='uploads/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file_name', models.CharField(max_length=250, null=True)),
                ('original_name', models.CharField(max_length=250, null=True)),
                ('display_name', models.CharField(max_length=250, null=True)),
                ('file_size', models.IntegerField(null=True)),
                ('file_size_mb', models.FloatField(null=True)),
                ('file_type', models.CharField(max_length=250, null=True)),
                ('file_extension', models.CharField(max_length=25, null=True)),
                ('file_display_type', models.CharField(max_length=25, null=True)),
                ('data', models.JSONField(null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('archived', 'Archived')], default='active', max_length=25)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
