from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='profile')
    go_account_id = models.CharField(max_length=10, blank=True, null=True)
