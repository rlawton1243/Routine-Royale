"""
Django Views
https://www.django-rest-framework.org/tutorial/3-class-based-views/
https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
"""
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets, status, renderers
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from royale.models import Client, EventParticipation, Task, Event, Clazz, UserAction, UserActionTypes
from royale.serializers import ClientSerializer, EventSerializer, TaskSerializer, UserSerializer, \
    EventParticipationSerializer, UserActionSerializer, UserActionTypesSerializer


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
        return request.user and request.user.is_authenticated


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
        if request.user.is_authenticated:
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
        if request.user.is_authenticated:
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

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def logged_in(self, request):
        """
        Get Client from logged in User PK
        :param request: HTTP Request object
        :return: HTTP Response
        """
        if request.user.is_authenticated:
            try:
                user = request.user
                client = Client.objects.filter(user=user)[0]
                serializer = ClientSerializer(instance=client)
                return Response(JSONRenderer().render(serializer.data), content_type='json')
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
            # Check if in Event already
            existing = EventParticipation.objects.filter(client=client, event=event)
            if len(existing) > 0:
                return Response({"error": f"Event Participation already exists! {existing}"},
                                status=status.HTTP_409_CONFLICT)
            # Check public or private
            if not event.is_public:
                key = request.data['key']
                assert key == event.event_key, f"Keys don't match! Given {key}, expecting {event.event_key}!"
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
            top = relevant[-5:]
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

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def all_event(self, request):
        """
        Returns all User's relevant tasks in an Event
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        qs = Task.objects.filter(event=request.data['event'])
        qs = qs.filter(event__eventparticipation__client__user=request.user).order_by('-id')
        serializer = TaskSerializer(instance=qs, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def remaining_event(self, request):
        """
        Returns all User's relevant tasks in an Event which are not complete
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        qs = Task.objects.filter(event=request.data['event'])
        qs = qs.filter(event__eventparticipation__client__user=request.user).order_by('-id')
        qs = qs.filter(~Q(eventparticipation__completed_tasks__in=qs))
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

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def complete(self, request):
        """
        Completes a Task for a User.
        Must see if the time is before the due time!
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        try:
            task = Task.objects.get(id=request.data['task'])
            event = task.event
            event_participation = EventParticipation.objects.filter(client__user=request.user)
            event_participation = event_participation.filter(event=event)[0]
            event_participation.completed_tasks.add(task)
            event_participation.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)  # TODO: Remove Debug

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def uncomplete(self, request):
        """
        Un-Completes a Task for a User.
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        try:
            task = Task.objects.get(id=request.data['task'])
            event = task.event
            event_participation = EventParticipation.objects.filter(client__user=request.user)
            event_participation = event_participation.filter(event=event)[0]
            event_participation.completed_tasks.remove(task)
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
    permission_classes = (permissions.IsAuthenticated,)

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


class UserActionViewSet(viewsets.ModelViewSet):
    queryset = UserAction.objects.all()
    serializer_class = UserActionSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    @action(methods=['GET'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def all(self, request):
        """
        Returns All of a Users daily actions created regardless of event
        :param request: The Django provided HTTP request from the User
        :return: HTTP Response
        """
        qs = UserAction.objects.filter(performer__user=request.user).order_by('-id')
        serializer = UserActionSerializer(instance=qs, many=True)
        return Response(JSONRenderer().render(serializer.data), content_type='json')

    @action(methods=['POST'], detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def take_action(self, request):
        """
        Creates an action with error checking
        :param request: 
        :return:
        """
        try:
            client = Client.objects.filter(user=request.user.id)[0]
            event = Event.objects.get(id=request.data['event'])
            target = Client.objects.get(id=request.data['target'])
            client_participations = EventParticipation.objects.filter(client=client, event=event)
            target_participations = EventParticipation.objects.filter(client=target, event=event)

            if len(client_participations) < 1:
                return Response({'error': f'Client Participation does not exist for {client} in {event}.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if len(target_participations) < 1:
                return Response({'error': f'Target Participation does not exist for {target} in {event}.'},
                                status=status.HTTP_400_BAD_REQUEST)

            client_participation = client_participations[0]
            target_participation = target_participations[0]
            action_type = UserActionTypes.objects.get(id=request.data['action_type'])

            # Check if in Event already
            existing = UserAction.objects.filter(performer=client_participation)
            if len(existing) > 0:
                print(f"Removing existing action for {client_participation}.")
                existing.delete()

            req = UserAction(action_type=action_type, performer=client_participation,
                             target=target_participation, event=event)
            req.save()
            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE, content_type='json')  # TODO: Remove Debug


class UserActionTypesViewSet(viewsets.ModelViewSet):
    queryset = UserActionTypes.objects.all()
    serializer_class = UserActionTypesSerializer
    permission_classes = [AllowAny,]


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
