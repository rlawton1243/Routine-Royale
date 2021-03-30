from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import random
from datetime import datetime
import constants


class EventParticipation(models.Model):

    id = models.AutoField(primary_key=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    health = models.IntegerField(default=100)
    energy = models.IntegerField(default=0)
    shield = models.IntegerField(default=0)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    selected_class = models.ForeignKey('Clazz', default=1, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return f"{self.id} -> {self.id}"


class Clazz(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    description = models.CharField(max_length=150)
    health = models.IntegerField(default=100)
    damage = models.IntegerField(default=10)


class Client(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    description = models.CharField(max_length=200, blank=True)
    owned_classes = models.ManyToManyField(Clazz)

    def __str__(self):
        return self.user.username


class TaskStep(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=30, blank=True)
    completed = models.BooleanField(default=False)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name}({self.id})"


class TaskSchedule(models.Model):

    id = models.AutoField(primary_key=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.id}: ' \
               f'{"0" if self.sunday else "1"}, ' \
               f'{"0" if self.monday else "1"}, ' \
               f'{"0" if self.tuesday else "1"}, ' \
               f'{"0" if self.wednesday else "1"}, ' \
               f'{"0" if self.thursday else "1"}, ' \
               f'{"0" if self.friday else "1"}, ' \
               f'{"0" if self.saturday else "1"}'


class Event(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    complete_date = models.DateTimeField(default=datetime.now, blank=True)

    @property
    def event_max_points(self):
        return Event.objects.get(pk=self.id).eventparticipation_set.all().count() * constants.POINTS_SCALE

    @property
    def event_key(self):
        return f'{self.id}-{random.randrange(100000, 999999)}'

    def __str__(self):
        return f"{self.name}({self.event_key})"


class Task(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)
    repeating = models.BooleanField(default=False)
    completion_time = models.DateTimeField(blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}({self.id})"


class UserAction(models.Model):

    id = models.AutoField(primary_key=True)
    action_type = models.IntegerField(default=0)
    performer = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='performer')
    target = models.OneToOneField(Client, on_delete=models.CASCADE)
