# Generated by Django 5.0.6 on 2024-10-25 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0007_alter_book_publishers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]