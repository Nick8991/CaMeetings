# Generated by Django 3.2.5 on 2021-12-20 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('non_members', '0002_rename_last_name_outsider_last_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outsider_loan',
            old_name='Outsider_Request',
            new_name='outsider_request',
        ),
    ]
