"""
Django Views
https://www.django-rest-framework.org/tutorial/3-class-based-views/
https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
"""
from django.db.models import Q
from django.http import Http404, HttpResponse
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from royale.models import Client, EventParticipation, TaskSchedule, TaskStep, Task, Event, UserAction, Clazz

from rest_framework import viewsets, status, renderers
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView

from django.contrib.auth.models import User

from royale.serializers import ClientSerializer, EventSerializer, TaskSerializer, UserSerializer, \
    EventParticipationSerializer


class AnonCreateAndUpdateOwnerOnly(permissions.BasePermission):
    """
    Custom permission:
        - allow anonymous POST
        - allow authenticated GET and PUT on *own* record
        - allow all actions for staff
    https://github.com/encode/django-rest-framework/issues/1067
    """

    def has_permission(self, request, view):
        return view.action == "create" or request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return view.action in ['retrieve', 'update',
                               'partial_update'] and obj.id == request.user.id or request.user.is_staff


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Client.objects.all().order_by('-id')
    serializer_class = ClientSerializer
    permission_classes = [AnonCreateAndUpdateOwnerOnly]

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def change_password(self, request):
        """
        Change Django Auth password.
        :param request: HTTP Request object
        :return: HTTP Response
        """
        if request.user.is_authenticated():
            try:
                user = request.user
                user.set_password(request['password'])
                user.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                print(e)
                return Response({"error": str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)  # TODO: Remove Debug
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def change_email(self, request):
        """
        Change Django Auth e-mail.
        :param request: HTTP Request object
        :return: HTTP Response
        """
        if request.user.is_authenticated():
            try:
                user = request.user
                user.email = request.data['email']
                user.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                print(e)
                return Response({"error": str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)  # TODO: Remove Debug
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Events to be viewed or edited.
    https://www.django-rest-framework.org/api-guide/viewsets/
    https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    # TODO: Override Delete

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def public(self, request):
        qs = Event.objects.filter(is_public=True).order_by('-id')
        serializer = EventSerializer(instance=qs, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def join_user(self, request):
        try:
            client = Client.objects.filter(user=request.user.id)[0]
            event = Event.objects.get(id=request.data['event'])
            if not event.is_public:
                key = request.data['key']
                assert key == event.event_key
            clazz = Clazz.objects.get(id=request.data['class'])
            req = EventParticipation(client=client, event=event, selected_class=clazz, health=clazz.health)
            req.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)  # TODO: Remove Debug

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def top_five(self, request):
        """
        Provides Top 5 Users sorted on Points in an Event
        :param request: HTTP Request object
        :return: HTTP Response
        """
        event = Event.objects.get(id=request.data['event'])
        relevant = EventParticipation.objects.filter(event=event)
        relevant = [(p, p.points) for p in relevant]
        relevant.sort(key=lambda x: x[1])
        if len(relevant) >= 5:
            top = relevant[:-5]
        else:
            top = relevant
        top = [p[0] for p in top]
        serializer = EventParticipationSerializer(instance=top, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json', status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def all(self, request):
        """
        Returns all User's joined Events
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        qs = Event.objects.filter(eventparticipation__client__user_id=request.user).order_by('-id')
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

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def all(self, request):
        """
        Returns all User's relevant tasks
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        qs = Task.objects.filter(event__eventparticipation__client__user=request.user).order_by('-id')
        serializer = TaskSerializer(instance=qs, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def remaining(self, request):
        """
        Returns tasks the User has not yet completed
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        user_tasks = Task.objects.filter(event__eventparticipation__client__user=request.user)
        incomplete = user_tasks.filter(~Q(eventparticipation__completed_tasks__in=user_tasks))

        serializer = TaskSerializer(instance=incomplete, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def complete(self, request):
        """
        Completes a Task for a User.
        Must see if the time is before the due time!
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        try:
            task = Task.objects.get(id=request.data['task'])
            event_participation = EventParticipation.objects.get(id=request.data['participation'])
            event_participation.completed_tasks.add(task)
            event_participation.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)  # TODO: Remove Debug


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [AnonCreateAndUpdateOwnerOnly, ]


class EventParticipationViewSet(viewsets.ModelViewSet):
    queryset = EventParticipation.objects.all()
    serializer_class = EventParticipationSerializer
    permission_classes = (AllowAny,)

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def all(self, request):
        """
        Returns all User's EventParticipation
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        qs = EventParticipation.objects.filter(client__user=request.user).order_by('-id')
        serializer = EventParticipationSerializer(instance=qs, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def test_login(request):
    """
    Creates EventParticipation based on Authenticated User and Provided Details
    """
    if request.method == "GET":
        return Response({
                "user": f"{request.user.id}"
        })
    if request.method == "POST":
        return Response({
                "hi": "post worked"
        })
