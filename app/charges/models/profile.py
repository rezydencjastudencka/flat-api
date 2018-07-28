from django.contrib.auth.models import User
from django.db import models

from charges.models.flat import Flat


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, on_delete=models.PROTECT)
