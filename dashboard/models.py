from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    limit = models.IntegerField(default=5)
    students = models.ManyToManyField(User)
