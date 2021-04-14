"""
Select relevant fields to serialize our objects.
"""

from royale.models import Client, EventParticipation, TaskSchedule, TaskStep, Task, Event, UserAction, Clazz
from rest_framework import serializers
from django.contrib.auth.models import User


class ClazzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clazz
        fields = ['id', 'name', 'description', 'health', 'damage']


class ClientSerializer(serializers.ModelSerializer):
    owned_classes = ClazzSerializer(many=True, required=False)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'user', 'email', 'points', 'description', 'owned_classes']


class EventParticipationSerializer(serializers.ModelSerializer):
    points = serializers.ReadOnlyField()

    class Meta:
        model = EventParticipation
        fields = ['id', 'client', 'health', 'energy', 'shield', 'event', 'selected_class', 'completed_tasks',
                  'completed_steps', 'total_completed', 'streak', 'points']


class SimpleEventParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventParticipation
        fields = ['id', 'client']


class TaskScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSchedule
        fields = ['id', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = ['id', 'name', 'description', 'task']


class TaskSerializer(serializers.ModelSerializer):
    class ScheduleField(serializers.Field):

        def to_representation(self, value):
            return str(value)

        def to_internal_value(self, data):
            t = TaskSchedule()
            t.sunday = 'U' in data
            t.monday = 'M' in data
            t.tuesday = 'T' in data
            t.wednesday = 'W' in data
            t.thursday = 'R' in data
            t.friday = 'F' in data
            t.saturday = 'S' in data

    schedule = ScheduleField(read_only=True)
    steps = TaskStepSerializer(source='taskstep_set', many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'repeating', 'due_time', 'event', 'schedule', 'steps']


class EventSerializer(serializers.ModelSerializer):
    participants = SimpleEventParticipationSerializer(source='eventparticipation_set', many=True, read_only=True)
    task_list = TaskSerializer(source='task_set', many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'is_public', 'owner', 'end_date', 'participants', 'task_list']


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
