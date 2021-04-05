"""
Select relevant fields to serialize our objects.
"""

from royale.models import Client, EventParticipation, TaskSchedule, TaskStep, Task, Event, UserAction
from rest_framework import serializers
from django.contrib.auth.models import User


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['user', 'points', 'description']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'is_public', 'owner', 'end_date']


class MultiEventSerializer(serializers.Serializer):

    def __init(self, events):
        self.events = events


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'repeating', 'due_time', 'event', 'schedule']


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
