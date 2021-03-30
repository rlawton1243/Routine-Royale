"""
Select relevant fields to serialize our objects.
"""

from royale.models import Client, EventParticipation, TaskSchedule, TaskSteps, Task, Event, UserActions
from rest_framework import serializers
from django.contrib.auth.models import User


class ClientSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Client
        fields = ['user', 'user_points', 'user_description']


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ['event_id', 'event_name', 'event_max_points', 'event_is_public', 'event_key', 'event_participators']


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ['task_id', 'task_name', 'task_description', 'task_repeating', 'task_completion_time',
                  'task_weekly_schedule', 'task_steps', 'associated_event']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)
