"""
Daily Cleanup will be a python script that does the following functions

For Every Event in System:

Check if event is complete

- if event is complete divy up points to all event participators
    Points = num total_completed + (.25 * streak * total_completed)
    - Don't delete anything right now we'll do that later


- otherwise...

1. Find all Tasks (and Steps) which were due on the current date
Tasks fetched, skipping steps until later

2. For Every EventParticipation related to the current Event:
    a. If the Task(s) (and steps) were completed increment total_completed
        Done and Tested!

    b. If ANY Tasks (or steps) were missed set streak to 0
        I. Else Increment streak by 1
         Done and Tested!

    c. Clear completed tasks and completed steps
         Done and Tested!
3. Set Task (and Step) Due Date/Times to next in Schedule if they were due Today and are repeating
"""

from django.core.management.base import BaseCommand, CommandError
from royale.models import Event, Task, EventParticipation, Client, UserAction
from datetime import *
from django.utils import timezone
import pytz


def event_end(event):
    """
        If event is complete, perform event completion tasks

        - Give points to all event participators
        Points = total_completed + (.25*streak*total_completed)
    """
    participators = event.eventparticipation_set.all()

    for participant in participators:
        client = Client.objects.get(eventparticipation__id=participant.id)
        client.points += (participant.total_completed + (.25 * participant.streak * participant.total_completed))
        client.save()
        participant.save()


def user_actions(event):
    """
    Goes through all the user actions for this event and does them

    Order of ops:
        1. Run through block actions to raise shield stat
        2. Run through attack actions and increment appropriate damage_taken
        3. Run through block actions again and reduce shield stat
        4. Clear this events UserActions (This might happen after all events
           have been run through

    :param event: Current event we're looking at the actions of
    :return: nothing
    """

    actions = UserAction.objects.all().filter(event=event.id)

    # Run through block actions first
    for action in actions.filter(action_type=2):
        participant = EventParticipation.objects.get(id=action.performer_id)

        participant.shield += .5
        participant.save()


class Command(BaseCommand):
    help = 'Performs the Daily Cleanup of Events and Assigns points to users'

    def handle(self, *args, **options):
        events = Event.objects.all()

        for event in events:
            print(event)
            today = timezone.now().replace(hour=23, minute=59)
            curr_weekday = datetime.today().weekday()
            tasks_due_today = event.task_set.filter(due_time__lte=today)

            # Gets QuerySet of all participators in current event
            participators = event.eventparticipation_set.all()

            for participant in participators:
                """
                For each participator in the event update task related stats
                """
                completed_today = participant.completed_tasks.all()
                print(participant)
                print(completed_today)

                participant.total_completed += len(list(completed_today))

                if set(completed_today) == set(tasks_due_today):
                    participant.streak += 1
                else:
                    participant.streak = 0

                participant.completed_tasks.clear()
                participant.save()

            print('Tasks in Event')
            for task in tasks_due_today:
                print(task)

                if task.schedule is None:
                    """
                    If Task does not have a schedule task will be deleted
                    
                    However we are not doing this until later
                    """

                    continue

                else:
                    """
                    If Task does have a schedule the tasks due date will be updated to the new due date
                    """

                    schedule = [1 if task.schedule.monday else 0,
                                1 if task.schedule.tuesday else 0,
                                1 if task.schedule.wednesday else 0,
                                1 if task.schedule.thursday else 0,
                                1 if task.schedule.friday else 0,
                                1 if task.schedule.saturday else 0,
                                1 if task.schedule.sunday else 0]
                    print(schedule)

                    # Monday updating through sunday
                    if curr_weekday == 0 and 1 in schedule[1:]:
                        task.due_time = task.due_time + timedelta(days=schedule[1:].index(1)-curr_weekday+1)
                    # Tuesday updating through sunday
                    elif curr_weekday == 1 and 1 in schedule[2:]:
                        task.due_time = task.due_time + timedelta(days=schedule[2:].index(1)-curr_weekday+1)
                    # Wednesday
                    elif curr_weekday == 2 and 1 in schedule[3:]:
                        task.due_time = task.due_time + timedelta(days=schedule[3:].index(1)-curr_weekday+1)
                    # Thursday
                    elif curr_weekday == 3 and 1 in schedule[4:]:
                        task.due_time = task.due_time + timedelta(days=schedule[4:].index(1)-curr_weekday+1)
                    # Friday
                    elif curr_weekday == 4 and 1 in schedule[5:]:
                        task.due_time = task.due_time + timedelta(days=schedule[5:].index(1)-curr_weekday+1)
                    # Saturday
                    elif curr_weekday == 5 and 1 in schedule[6]:
                        task.due_time = task.due_time + timedelta(days=schedule[6:].index(1)-curr_weekday+1)
                    # Sunday and there is a 1 in the schedule and repeating is enabled it goes to next available
                    if task.repeating and 1 in schedule:
                        task.due_time = task.due_time + timedelta(days=schedule.index(1)+1)
                    elif not task.repeating:
                        pass

                task.save()
            print('\n')
            # Check if event is completed
            if event.end_date <= today:
                event_end(event)
                continue
