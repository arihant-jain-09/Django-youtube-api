from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Hall(models.Model):
    title=models.CharField(max_length=255)
    user=models.ForeignKey(User,related_name='user',on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Video(models.Model):
    title=models.CharField(max_length=255)
    url=models.URLField()
    youtube_id=models.CharField(max_length=255)
    hall=models.ForeignKey(Hall,related_name="video",on_delete=models.CASCADE)
    def __str__(self):
        return self.title
