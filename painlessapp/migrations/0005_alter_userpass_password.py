# Generated by Django 5.1.2 on 2024-11-24 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('painlessapp', '0004_alter_folder_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpass',
            name='password',
            field=models.CharField(help_text='This is your password you want to store.', max_length=255),
        ),
    ]
