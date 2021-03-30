from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import random
from datetime import datetime
import constants


class EventParticipation(models.Model):
    """
    Defines a Client participation in an Event.
    """

    id = models.AutoField(primary_key=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    health = models.IntegerField(default=100)
    energy = models.IntegerField(default=0)
    shield = models.IntegerField(default=0)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    selected_class = models.ForeignKey('Clazz', default=1, on_delete=models.SET_DEFAULT)
    completed_tasks = models.ManyToManyField('Task')
    completed_steps = models.ManyToManyField('TaskStep')
    total_completed = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{str(self.client)} -> {str(self.event)}"


class Clazz(models.Model):
    """
    Defines selectable/purchasable Class (i.e. Health and DMG)
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    description = models.CharField(max_length=150)
    health = models.IntegerField(default=100)
    damage = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.name} (H:{self.health}, D:{self.damage})"


class Client(models.Model):
    """
    Defines a RR client, relating to the Django auth backend.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    description = models.CharField(max_length=200, blank=True)
    owned_classes = models.ManyToManyField(Clazz, blank=True)

    def __str__(self):
        self.user: User
        return self.user.username


class TaskStep(models.Model):
    """
    Defines a step as part of a Task.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=30, blank=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{str(self.task)}: {self.name}"


class TaskSchedule(models.Model):
    """
    Defines a task's Schedule
    """

    id = models.AutoField(primary_key=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    def __str__(self):
        return f'{"U" if self.sunday else ""}' \
               f'{"M" if self.monday else ""}' \
               f'{"T" if self.tuesday else ""}' \
               f'{"W" if self.wednesday else ""}' \
               f'{"R" if self.thursday else ""}' \
               f'{"F" if self.friday else ""}' \
               f'{"S" if self.saturday else ""}'


class Event(models.Model):
    """
    Defines an Event containing Tasks, with participating Users.
    """

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
        return f"{self.name} ({self.event_key})"


class Task(models.Model):
    """
    Defines a Task as part of an Event.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)
    repeating = models.BooleanField(default=False)
    schedule = models.ForeignKey(TaskSchedule, null=True, blank=True, on_delete=models.SET_NULL)
    due_time = models.DateTimeField(blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.event)}: {self.name}"


class UserAction(models.Model):
    """
    Defines a User Action (daily) as part of an Event.
    """

    id = models.AutoField(primary_key=True)
    action_type = models.IntegerField(default=0)
    performer = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='performer')
    target = models.OneToOneField(Client, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.performer)} -({str(self.action_type)})-> {str(self.target)}"
