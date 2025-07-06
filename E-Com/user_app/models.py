from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.username
