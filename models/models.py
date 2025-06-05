from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


    
class videoUserManager(BaseUserManager):
    def createUser(self, username, password):
        user = self.model(username=username, password=password)
        user.save(using=self._db)
        return user

    def deleteUser(self, username):
        try:
            user = self.get(username=username)
            user.delete()
            return True
        except self.model.DoesNotExist:
            return False

class videoUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=50, blank=False)
    profile_picture = models.ImageField(upload_to=f'profilePictures/{username}/', null=True)
    bio = models.TextField()
    objects = videoUserManager()  
    USERNAME_FIELD = 'username'


class tag(models.Model):
    tagName = models.CharField(max_length=50, unique=True)
    
class video(models.Model):
    title = models.TextField(blank=False)
    description = models.TextField(blank=True)

    #video will refer to a directory on the server
    video = models.TextField(blank=False, unique=True)

    views = models.IntegerField()

    tags = models.ManyToManyField(tag, blank=True, related_name='videos')
