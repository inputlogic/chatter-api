# Generated by Django 3.0.6 on 2020-05-20 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatter', '0004_auto_20200519_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='password_hash',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]