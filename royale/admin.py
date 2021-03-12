from django.contrib import admin

from .models import User, UserActions, Task, TaskSteps, TaskSchedule, Event, EventParticipation

admin.site.register(User)
admin.site.register(UserActions)
admin.site.register(Task)
admin.site.register(TaskSteps)
admin.site.register(TaskSchedule)
admin.site.register(Event)
admin.site.register(EventParticipation)
