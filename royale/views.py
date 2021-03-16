"""
Django Views
"""
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from royale.models import User, EventParticipation, TaskSchedule, TaskSteps, Task, Event, UserActions

from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView

from royale.serializers import UserSerializer, EventSerializer, TaskSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-user_id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Events to be viewed or edited.
    """
    queryset = Event.objects.all().order_by('-event_id')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Task.objects.all().order_by('-task_id')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
