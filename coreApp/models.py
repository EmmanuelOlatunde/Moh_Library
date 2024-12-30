from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.CharField(max_length=50)
    description = models.TextField(max_length=150)
    cover_image = models.ImageField(blank=True, null=True)
    publish_date = models.DateField(max_length=50)
    isbn = models.IntegerField()
    publishers = models.CharField(max_length=100)
    file = models.FileField(blank=True, null=True)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class BookmarkedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')