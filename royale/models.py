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
    shield = models.IntegerField(default=1)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    selected_class = models.ForeignKey('Clazz', default=1, on_delete=models.SET_DEFAULT)
    damage_taken = models.IntegerField(default=0)
    attack_damage = models.IntegerField(default=10)
    completed_tasks = models.ManyToManyField('Task', blank=True)
    completed_steps = models.ManyToManyField('TaskStep', blank=True)
    total_completed = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)

    @property
    def points(self):
        return self.total_completed + (.25 * self.streak * self.total_completed)

    def save(self, *args, **kwargs):
        self.health = Clazz.objects.get(pk=self.selected_class_id).health - self.damage_taken
        self.attack_damage = Clazz.objects.get(pk=self.selected_class_id).damage
        super(EventParticipation, self).save(*args, **kwargs)

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
        return f'{"M" if self.monday else ""}' \
               f'{"T" if self.tuesday else ""}' \
               f'{"W" if self.wednesday else ""}' \
               f'{"R" if self.thursday else ""}' \
               f'{"F" if self.friday else ""}' \
               f'{"S" if self.saturday else ""}' \
               f'{"U" if self.sunday else ""}'


class Event(models.Model):
    """
    Defines an Event containing Tasks, with participating Users.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    end_date = models.DateTimeField(default=datetime.now, blank=True)
    random_seed = models.CharField(max_length=6, default=0, blank=True)

    @property
    def event_max_points(self):
        return Event.objects.get(pk=self.id).eventparticipation_set.all().count() * constants.POINTS_SCALE

    @property
    def event_key(self):
        return f'{self.id}-{self.random_seed}'

    def create_rando(self):
        self.random_seed = random.randrange(100000, 999999)

    def save(self, *args, **kwargs):
        self.create_rando()
        super(Event, self).save(*args, **kwargs)

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
    action_type = models.ForeignKey('UserActionTypes', default=1, on_delete=models.SET_DEFAULT)
    performer = models.ForeignKey(EventParticipation, related_name='performer', on_delete=models.CASCADE, default=1)
    target = models.ForeignKey(EventParticipation, on_delete=models.CASCADE, default=1, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.performer)} -({str(self.action_type)})-> {str(self.target)}"


class UserActionTypes(models.Model):
    """
    Functions similar to Clazz, outline/storage for the different types of actions we are allowing

    :var id will be used to identify which action the user wants to perform in daily_cleanup.py
    :var action and description will be used GUI side to relay what the action does to the user
    :var energy_cost is the energy cost duh...
    """

    id = models.AutoField(primary_key=True)
    action = models.CharField(default='Attack', max_length=20)
    description = models.CharField(max_length=100, default='')
    energy_cost = models.IntegerField(default=1)

    def __str__(self):
        return self.action
