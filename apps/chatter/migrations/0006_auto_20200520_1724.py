# Generated by Django 3.0.6 on 2020-05-20 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatter', '0005_room_password_hash'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='password_hash',
            new_name='password',
        ),
    ]
