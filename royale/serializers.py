"""
Select relevant fields to serialize our objects.
"""

from royale.models import User, EventParticipation, TaskSchedule, TaskSteps, Task, Event, UserActions
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'user_points', 'user_description']

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ['event_id', 'event_name', 'event_max_points', 'event_is_public', 'event_key', 'event_participators',
                  'task_list']


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ['task_id', 'task_name', 'task_description', 'task_repeating', 'task_completion_time',
                  'task_weekly_schedule', 'task_steps']

