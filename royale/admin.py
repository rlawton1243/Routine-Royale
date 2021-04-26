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
    model = TaskStep
    extra = 0


class TaskAdminInline(admin.TabularInline):
    model = Task
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    inlines = (TaskStepAdminInline, )


class EventAdmin(admin.ModelAdmin):
    inlines = (TaskAdminInline,)


admin.site.register(Task, TaskAdmin)
admin.site.register(Event, EventAdmin)
