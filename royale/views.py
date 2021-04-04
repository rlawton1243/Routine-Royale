"""
Django Views
https://www.django-rest-framework.org/tutorial/3-class-based-views/
https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
"""
from django.http import Http404, HttpResponse
from rest_framework.decorators import api_view, action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from royale.models import Client, EventParticipation, TaskSchedule, TaskStep, Task, Event, UserAction

from rest_framework import viewsets, status, renderers
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView


from django.contrib.auth.models import User

from royale.serializers import ClientSerializer, EventSerializer, TaskSerializer, UserSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Client.objects.all().order_by('-id')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Events to be viewed or edited.
    https://www.django-rest-framework.org/api-guide/viewsets/
    https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def public(self, request):
        qs = Event.objects.filter(is_public=True).order_by('-id')
        serializer = EventSerializer(instance=qs, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    https://stackoverflow.com/questions/53760772/how-to-create-a-custom-action-endpoint-that-corresponds-to-put-and-executes-a-fu
    """
    queryset = Task.objects.all().order_by('-id')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientCreateAPIView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (AllowAny,)


class EventParticipationViewSet(viewsets.ModelViewSet):
    queryset = EventParticipation.objects.all()
    #serializer_class = EventParticipationSerializer
    permission_classes = (AllowAny, )

    @action(methods=['post'], detail=True)
    def join_event(self, request, pk=None):
        pass



@api_view(['POST', 'GET'])
def join_event(request):
    """
    Creates EventParticipation based on Authenticated User and Provided Details
    """
    if request.method == "GET":
        return Response({
            "message": "Hello, world!"
        })

