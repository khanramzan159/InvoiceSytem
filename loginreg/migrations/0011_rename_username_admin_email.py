# Generated by Django 5.0.1 on 2024-02-16 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loginreg', '0010_remove_historicalinvoice_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admin',
            old_name='username',
            new_name='email',
        ),
    ]
