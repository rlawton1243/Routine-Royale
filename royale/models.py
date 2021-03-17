from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_points = models.IntegerField(default=0)
    user_description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username


class EventParticipation(models.Model):
    participation_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    user_health = models.IntegerField(default=100)
    user_energy = models.IntegerField(default=0)
    user_shield = models.IntegerField(default=0)
    user_class = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user_id} -> {self.participation_id}"


class TaskSteps(models.Model):
    step_id = models.AutoField(primary_key=True)
    step_name = models.CharField(max_length=30)
    step_description = models.CharField(max_length=30, blank=True)
    step_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.step_name}({self.step_id})"


class TaskSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    scheduled_on_monday = models.BooleanField(default=False)
    scheduled_on_tuesday = models.BooleanField(default=False)
    scheduled_on_wednesday = models.BooleanField(default=False)
    scheduled_on_thursday = models.BooleanField(default=False)
    scheduled_on_friday = models.BooleanField(default=False)
    scheduled_on_saturday = models.BooleanField(default=False)
    scheduled_on_sunday = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.schedule_id}: ' \
               f'{"0" if self.scheduled_on_sunday else "1"}, ' \
               f'{"0" if self.scheduled_on_monday else "1"}, ' \
               f'{"0" if self.scheduled_on_tuesday else "1"}, ' \
               f'{"0" if self.scheduled_on_wednesday else "1"}, ' \
               f'{"0" if self.scheduled_on_thursday else "1"}, ' \
               f'{"0" if self.scheduled_on_friday else "1"}, ' \
               f'{"0" if self.scheduled_on_saturday else "1"}'


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=30)
    task_description = models.CharField(max_length=200, blank=True)
    task_repeating = models.BooleanField(default=False)
    task_completion_time = models.DateTimeField(blank=True)
    task_weekly_schedule = models.ForeignKey(TaskSchedule, on_delete=models.CASCADE, null=True)
    task_steps = models.ForeignKey(TaskSteps, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.task_name}({self.task_id})"


# TODO: Add create_key function that combines event_id with a hash of name to be unique
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=30)
    event_max_points = models.IntegerField(default=0)
    event_is_public = models.BooleanField(default=True)
    event_key = models.CharField(max_length=8, unique=True)
    event_participators = models.ForeignKey(EventParticipation, on_delete=models.CASCADE)
    task_list = models.ForeignKey(Task, on_delete=models.CASCADE)
    event_owner = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.event_name}({self.event_key})"


class UserActions(models.Model):
    user_action_id = models.AutoField(primary_key=True)
    user_action_type = models.IntegerField(default=0)
    user_action_performer = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='performer')
    user_action_target = models.OneToOneField(Client, on_delete=models.CASCADE)
