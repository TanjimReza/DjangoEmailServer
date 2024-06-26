# Generated by Django 5.0.5 on 2024-05-20 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otphome', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BandwidthLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('function_name', models.CharField(max_length=255)),
                ('bytes_sent', models.BigIntegerField()),
                ('bytes_received', models.BigIntegerField()),
                ('total_bytes', models.BigIntegerField()),
                ('total_mb', models.FloatField()),
            ],
        ),
    ]
