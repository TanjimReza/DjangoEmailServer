# Generated by Django 5.0.5 on 2024-05-09 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('from_email', models.EmailField(blank=True, db_index=True, max_length=254, null=True)),
                ('to_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('subject', models.CharField(blank=True, max_length=254, null=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('date_time', models.DateTimeField(blank=True, null=True)),
                ('profile', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('login_otp', models.CharField(blank=True, max_length=254, null=True)),
                ('household_link', models.CharField(blank=True, max_length=254, null=True)),
                ('tag', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
