from django.conf import settings
from django.db import models
from gcm import GCM


# Create your models here.
class Counter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    counter = models.IntegerField()

    def save(self, *args, **kwargs):
        gcm = GCM(settings.GCM_KEY)
        data = {'type': 'notify'}
        res = gcm.send_topic_message(topic="counter_"+self.name, data=data)
        super(Counter, self).save(*args, **kwargs)

    @staticmethod
    def modify_and_get(amount, name):
        counter = Counter.objects.get(name=name)
        counter.counter += amount
        counter.save()
        return counter
