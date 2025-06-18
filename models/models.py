from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import datetime as time


class videoUserManager(BaseUserManager):
    def createUser(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.createUser(username, password, **extra_fields)

    def deleteUser(self, username):
        try:
            user = self.get(username=username)
            user.delete()
            return True
        except self.model.DoesNotExist:
            return False


class videoUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=128, blank=False)
    creationDate = models.DateTimeField(default=time.datetime.now())
    pfp = models.TextField(null=True, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    followCount = models.IntegerField(default=0)
    following = models.ManyToManyField('videoUser',related_name='followers', blank=True)
    videos = models.ManyToManyField('video',related_name='authored_videos', blank=True)

    objects = videoUserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username



class video(models.Model):
    title = models.TextField(blank=False)
    description = models.TextField(null=True)

    #video will refer to a directory on the server
    video = models.TextField(blank=False, unique=True)

    views = models.IntegerField(default=0)

    author = models.ForeignKey(
        videoUser,
        related_name='author',
        on_delete=models.CASCADE,
    )

    cover = models.TextField(null=True, unique=True)

    date = models.DateTimeField(default=time.datetime.now())

    videoLength = models.FloatField(null=False, blank=False)


class tag(models.Model):
    tagName = models.CharField(max_length=50, unique=True, blank=False)

    videos = models.ManyToManyField(video, blank=True)

@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_auth_token(sender, instance, **kwargs):
    try:
        Token.objects.get(user=instance).delete()
    except Token.DoesNotExist:
        pass
