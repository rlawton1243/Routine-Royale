from django.contrib import admin

from .models import Client, Clazz, Event, EventParticipation, Task, TaskStep, TaskSchedule, UserAction

admin.site.register(Client)
admin.site.register(UserAction)
admin.site.register(Task)
admin.site.register(TaskStep)
admin.site.register(TaskSchedule)
admin.site.register(Event)
admin.site.register(EventParticipation)
admin.site.register(Clazz)


# class EventParticipation(admin.ModelAdmin):
#     model = EventParticipation
#     list_display = ['__']
