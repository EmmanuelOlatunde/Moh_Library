# Generated by Django 5.0.6 on 2024-10-25 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0009_book_book_summary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='book_summary',
            new_name='summary',
        ),
    ]