# Generated by Django 5.1.2 on 2024-10-26 06:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('painlessapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpass',
            name='folder',
            field=models.ForeignKey(help_text='Select one of your folders to categorize the password, or select none.', on_delete=django.db.models.deletion.CASCADE, to='painlessapp.folder'),
        ),
    ]
