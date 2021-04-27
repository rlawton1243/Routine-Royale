from django.contrib import admin

from .models import Client, Clazz, Event, EventParticipation, Task, TaskStep, TaskSchedule, UserAction, UserActionTypes

admin.site.register(Client)
admin.site.register(UserAction)
admin.site.register(TaskStep)
admin.site.register(TaskSchedule)
admin.site.register(EventParticipation)
admin.site.register(Clazz)
admin.site.register(UserActionTypes)


class TaskStepAdminInline(admin.TabularInline):
    """
    Provides an inline display for steps in a Task
    """
    model = TaskStep
    extra = 0


class TaskAdminInline(admin.TabularInline):
    """
    Provides an inline display for Tasks in an Event or Participation
    """
    model = Task
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    """
    Overrides default Task view
    """
    inlines = (TaskStepAdminInline,)


class EventAdmin(admin.ModelAdmin):
    """
    Overrides default Event view
    """
    inlines = (TaskAdminInline,)


admin.site.register(Task, TaskAdmin)
admin.site.register(Event, EventAdmin)
