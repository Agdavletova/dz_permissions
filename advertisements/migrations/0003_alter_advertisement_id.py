# Generated by Django 5.1.1 on 2024-10-04 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0002_alter_advertisement_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
