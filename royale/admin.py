from django.contrib import admin

from .models import Client, UserActions, Task, TaskSteps, TaskSchedule, Event, EventParticipation

admin.site.register(Client)
admin.site.register(UserActions)
admin.site.register(Task)
admin.site.register(TaskSteps)
admin.site.register(TaskSchedule)
admin.site.register(Event)
admin.site.register(EventParticipation)
