# Generated by Django 5.0.6 on 2024-10-24 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('authors', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=300)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('publish_date', models.DateField(max_length=50)),
                ('isbn', models.CharField(max_length=25)),
                ('publishers', models.TextField(max_length=50)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.DeleteModel(
            name='books',
        ),
    ]
