from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

User._meta.get_field('email')._unique = True

class Device(models.Model):
    name = models.CharField(max_length=100)
    num_used = models.IntegerField(default=0)
    max_uses = models.IntegerField()
    available = models.BooleanField(default=True)
    description = models.CharField(max_length=1000)


class Room(models.Model):
    room_number = models.IntegerField(validators=[
            MaxValueValidator(1000),
            MinValueValidator(1)])
    description = models.CharField(max_length=1000)
    
class Rental(models.Model):
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    return_time = models.DateTimeField()

    def room_number(self):
        return self.room_id.room_number
    
    def device_name(self):
        return self.device_id.name
    

