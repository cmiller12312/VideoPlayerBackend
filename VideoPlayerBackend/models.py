from django.db import models
from django.contrib.auth.models import User

class videoUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
class video(models.Model):
    title = models.TextField(blank=False)
    description = models.TextField(blank=True)

    #video will refer to a directory on the server
    video = models.TextField(blank=False)