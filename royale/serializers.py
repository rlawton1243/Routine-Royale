"""
Select relevant fields to serialize our objects.
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from royale.models import Client, EventParticipation, TaskSchedule, TaskStep, Task, Event, UserAction, \
    Clazz, UserActionTypes


class ClazzSerializer(serializers.ModelSerializer):
    """
    Serializes a Class object.
    """

    class Meta:
        model = Clazz
        fields = ['id', 'name', 'description', 'health', 'damage']


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializes a Client object.
    """
    owned_classes = ClazzSerializer(many=True, required=False)
    email = serializers.CharField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'user', 'username', 'email', 'points', 'description', 'owned_classes']


class EventParticipationSerializer(serializers.ModelSerializer):
    """
    Serializes an Event object.
    """
    points = serializers.ReadOnlyField()
    username = serializers.CharField(source='client.user.username', read_only=True)

    class Meta:
        model = EventParticipation
        fields = ['id', 'client', 'username', 'health', 'energy', 'shield', 'event', 'selected_class',
                  'completed_tasks',
                  'completed_steps', 'total_completed', 'streak', 'points']


class SimpleEventParticipationSerializer(serializers.ModelSerializer):
    """
    Minimally serializes an Event Participation.
    """
    username = serializers.CharField(source='client.user.username', read_only=True)

    class Meta:
        model = EventParticipation
        fields = ['id', 'client', 'username']


class TaskScheduleSerializer(serializers.ModelSerializer):
    """
    Serializes a Task Schedule.
    """

    class Meta:
        model = TaskSchedule
        fields = ['id', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


class TaskStepSerializer(serializers.ModelSerializer):
    """
    Serializes a Task Step.
    """

    class Meta:
        model = TaskStep
        fields = ['id', 'name', 'description', 'task']


class UserActionSerializer(serializers.ModelSerializer):
    """
    Serializes a User Action.
    """

    class Meta:
        model = UserAction
        fields = ['id', 'action_type', 'performer', 'target', 'event']


class UserActionTypesSerializer(serializers.ModelSerializer):
    """
    Serializes a User Action Type.
    """

    class Meta:
        model = UserActionTypes
        fields = ['id', 'action', 'description', 'energy_cost']


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializes a Task.
    """

    class ScheduleField(serializers.Field):
        """
        Represents a Task Schedule as a string.
        """

        def to_representation(self, value):
            """
            Converts a value to its string encoding.
            :param value: Value to convert
            :return: string representation
            """
            return str(value)

        def to_internal_value(self, data):
            """
            Converts a string representation to a TaskSchedule object.
            :param data: str input data
            :return: TaskSchedule from string
            """
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
    """
    Serializes an EventSerializer object.
    """
    participants = SimpleEventParticipationSerializer(source='eventparticipation_set', many=True, read_only=True)
    task_list = TaskSerializer(source='task_set', many=True, read_only=True)
    event_key = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'is_public', 'owner', 'end_date', 'participants', 'task_list', 'event_key']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes a User object.
    """

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
        """
        Creates a User from validated data.
        :param validated_data: dictionary of input validated data
        :return: User object
        """
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Updates a User instance from validated data.
        :param instance: Instance to update
        :param validated_data: dictionary of input validated data
        :return: Updated User object
        """
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)
