# Generated by Django 5.0.6 on 2024-10-25 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0005_alter_book_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=20),
        ),
    ]
