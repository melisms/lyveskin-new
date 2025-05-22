from django.db import models
from django.contrib.auth.models import User
from item.models import Item

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default_profile.png')
    favorites = models.ManyToManyField(Item, related_name='favorited_by', blank=True)
    email_verified = models.BooleanField(default=False)
