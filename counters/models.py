from django.db import models


# Create your models here.
class Counter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    counter = models.IntegerField()

    @staticmethod
    def modify_and_get(amount, name):
        counter = Counter.objects.get(name=name)
        counter.counter += amount
        counter.save()
        return counter
