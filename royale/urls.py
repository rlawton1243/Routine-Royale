from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from royale import views

router = routers.DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'users', views.UserViewSet)
#router.register(r'test', views.join_event)
router.register(r'participations', views.EventParticipationViewSet)
router.register(r'useraction', views.UserActionViewSet)
router.register(r'useractiontypes', views.UserActionTypesViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('test_login/', views.test_login)
]
