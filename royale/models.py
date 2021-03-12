import datetime
from django.db import models
from django.utils import timezone


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=30, unique=True)
    user_points = models.IntegerField(default=0)
    user_description = models.CharField(max_length=200)

    def __str__(self):
        return self.user_name


class EventParticipation(models.Model):
    participation_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_health = models.IntegerField(default=100)
    user_energy = models.IntegerField(default=0)
    user_shield = models.IntegerField(default=0)
    user_class = models.IntegerField(default=0)


class TaskSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    scheduled_on_monday = models.BooleanField(default=False)
    scheduled_on_tuesday = models.BooleanField(default=False)
    scheduled_on_wednesday = models.BooleanField(default=False)
    scheduled_on_thursday = models.BooleanField(default=False)
    scheduled_on_friday = models.BooleanField(default=False)
    scheduled_on_saturday = models.BooleanField(default=False)
    scheduled_on_sunday = models.BooleanField(default=False)


class TaskSteps(models.Model):
    step_id = models.AutoField(primary_key=True)
    step_name = models.CharField(max_length=30)
    step_description = models.CharField(max_length=30)
    step_completed = models.BooleanField(default=False)


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=30)
    task_description = models.CharField(max_length=200)
    task_repeating = models.BooleanField(default=False)
    task_completion_time = models.DateTimeField()
    task_weekly_schedule = models.OneToOneField(TaskSchedule, on_delete=models.CASCADE)
    task_steps = models.ForeignKey(TaskSteps, on_delete=models.CASCADE)

    def __str__(self):
        return self.task_name


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=30)
    event_max_points = models.IntegerField(default=0)
    event_is_public = models.BooleanField(default=True)
    event_key = models.CharField(max_length=8)
    event_participators = models.ForeignKey(EventParticipation, on_delete=models.CASCADE)
    task_list = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.event_name


class UserActions(models.Model):
    user_action_id = models.AutoField(primary_key=True)
    user_action_type = models.IntegerField(default=0)
    user_action_performer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='performer')
    user_action_target = models.OneToOneField(User, on_delete=models.CASCADE)
