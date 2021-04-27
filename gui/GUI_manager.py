import kivy

kivy.require('2.0.0')

from network import NetworkManager
from shared import Shared
from functools import partial
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown


def popup_widget(popup_label, popup_title, close_button_label='Dismiss'):
    layout = BoxLayout(orientation='vertical')
    popup_content = Label(text=f'{popup_label}',
                          valign='center', halign='center')
    close_button = Button(text=f'{close_button_label}',
                          size_hint=(None, None), size=(80, 40),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})
    layout.add_widget(popup_content)
    layout.add_widget(close_button)
    popup = Popup(title=f'{popup_title}', title_align='center',
                  content=layout,
                  size_hint=(None, None), size=(300, 200),
                  auto_dismiss=False)
    close_button.bind(on_press=popup.dismiss)
    popup.open()


def get_all_events(shared):
    events = shared.nm.get('/events/', True)
    event_results = events['results']
    curr_page = 1
    while events['next'] is not None:
        curr_page += 1
        events = shared.nm.get(f'/events/?page={curr_page}', True)
        for event in events['results']:
            event_results.append(event)
    return event_results


class RoutineLogin(Screen):

    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)

    def LoginAccount(self, userInput, password):
        logged_in = self.shared.nm.login(userInput, password)
        if not logged_in:
            popup_widget('Invalid credentials, try again.', 'Login failed')
        return logged_in


class RoutineCreate(Screen):

    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)

    def CreateAccount(self, username, password):
        userID = None
        try:
            userID = self.shared.nm.add_user(username, password)
            self.shared.nm.add_client(userID)
        except OSError:
            popup_widget('User already exists, try again.', 'Account Creation failed')
        if userID is not None:
            popup_widget('Account created successfully!', 'Account Created!')


class RoutineMain(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)
        self.tasks_info = []

        self.events_popup = None

    def list_user_events(self):
        events = self.shared.nm.get('/events/all/', True)
        unique_events = []
        for event in events:
            if event in unique_events:
                break
            else:
                unique_events.append(event)
        scroll_layout = ScrollView(size_hint=(1, None), size=(600, 435))
        outside_scroll = GridLayout(rows=2, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        inside_scroll = GridLayout(cols=4, size_hint_y=None, spacing=20)
        inside_scroll.bind(minimum_height=inside_scroll.setter('height'))
        dismiss_button = Button(text='Dismiss',
                                size_hint=(None, None), size=(80, 40),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
        for event in unique_events:
            raw_end_date = event['end_date']
            final_end_date = raw_end_date.split('-')
            time = final_end_date[2].split('T')
            time = time[:8]
            final_end_date[2] = time[0]
            final_end_date.append(time[1])
            final_end_date[3] = final_end_date[3].replace('Z', '')
            final_end_date[3] = final_end_date[3][:8]
            id_label = Label(text=f'ID: {event["id"]}',
                             valign='center', halign='center',
                             size_hint=(None, None), size=(80, 40))
            title_label = Label(text=f'Name: {event["name"]}')
            end_date_label = Label(text=f'\nEnd date info:\nMonth: {final_end_date[1]} Day: {final_end_date[2]}\n'
                                        f'Year: {final_end_date[0]} Time: {final_end_date[3]}')
            view_button = Button(text='View Event',
                                 size_hint=(None, None), size=(80, 40),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5})
            view_button.bind(on_press=partial(self.switch_screen, event))
            inside_scroll.add_widget(id_label)
            inside_scroll.add_widget(title_label)
            inside_scroll.add_widget(end_date_label)
            inside_scroll.add_widget(view_button)
        inside_scroll.add_widget(dismiss_button)
        scroll_layout.add_widget(inside_scroll)
        outside_scroll.add_widget(scroll_layout)
        self.events_popup = Popup(title='Public Events', title_align='center',
                                  content=outside_scroll,
                                  size_hint=(None, None), size=(600, 500),
                                  auto_dismiss=False)
        dismiss_button.bind(on_release=self.events_popup.dismiss)
        self.events_popup.open()

    def switch_screen(self, event, instance):
        for user in self.shared.nm.top_five(event['id']):
            if user['username'] == self.shared.username:
                self.shared.health_amount_label.text = str(user['health'])
        self.events_popup.dismiss()
        self.shared.req_event_title = event['name']
        self.shared.event_name_label.text = event['name']
        self.shared.event_id = event['id']
        self.shared.complete, self.shared.incomplete = self.shared.nm.get_event_tasks(event['id'])
        scroll = self.shared.event_details_scroll
        for widget in self.shared.event_details_widgets:
            scroll.remove_widget(widget)
        self.shared.event_details_widgets = []
        for task in self.shared.complete:
            task_desc = Label(text=f'{task["name"]}', size_hint=(None, None), size=(250, 40),
                              pos_hint={'center_x': 0.25, 'top': 0.1})
            task_comp = CheckBox(active=True)

            scroll.add_widget(task_desc)
            scroll.add_widget(task_comp)
            self.shared.event_details_widgets.append(task_desc)
            self.shared.event_details_widgets.append(task_comp)
            task['checkbox'] = task_comp
        for task in self.shared.incomplete:
            task_desc = Label(text=f'{task["name"]}', size_hint=(None, None), size=(250, 40),
                              pos_hint={'center_x': 0.25, 'top': 0.1})
            task_comp = CheckBox(active=False)
            scroll.add_widget(task_desc)
            scroll.add_widget(task_comp)
            self.shared.event_details_widgets.append(task_desc)
            self.shared.event_details_widgets.append(task_comp)
            task['checkbox'] = task_comp
        self.manager.transition.direction = 'down'
        self.manager.current = 'eventDetails'

    def list_public_events(self):
        event_results = get_all_events(self.shared)
        scroll_layout = ScrollView(size_hint=(1, None), size=(600, 435))
        outside_scroll = GridLayout(rows=2, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        inside_scroll = GridLayout(cols=4, size_hint_y=None, spacing=20)
        inside_scroll.bind(minimum_height=inside_scroll.setter('height'))
        dismiss_button = Button(text='Dismiss',
                                size_hint=(None, None), size=(80, 40),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
        for event in event_results:
            if event['is_public']:
                raw_end_date = event['end_date']
                final_end_date = raw_end_date.split('-')
                time = final_end_date[2].split('T')
                final_end_date[2] = time[0]
                final_end_date.append(time[1])
                final_end_date[3] = final_end_date[3].replace('Z', '')
                final_end_date[3] = final_end_date[3][:8]
                id_label = Label(text=f'ID: {event["id"]}',
                                 valign='center', halign='center',
                                 size_hint=(None, None), size=(80, 40))
                title_label = Label(text=f'Name: {event["name"]}')
                end_date_label = Label(
                    text=f'\nEnd date info:\nMonth: {final_end_date[1]} Day: {final_end_date[2]}\n'
                         f'Year: {final_end_date[0]} Time: {final_end_date[3]}')
                join_button = Button(text='Join Event',
                                     size_hint=(None, None), size=(80, 40),
                                     pos_hint={'center_x': 0.5, 'center_y': 0.5})
                join_button.bind(on_press=partial(self.join_public_event, event['id']))
                inside_scroll.add_widget(id_label)
                inside_scroll.add_widget(title_label)
                inside_scroll.add_widget(end_date_label)
                inside_scroll.add_widget(join_button)
        inside_scroll.add_widget(dismiss_button)
        scroll_layout.add_widget(inside_scroll)
        outside_scroll.add_widget(scroll_layout)
        events_popup = Popup(title='User Events', title_align='center',
                             content=outside_scroll,
                             size_hint=(None, None), size=(600, 500),
                             auto_dismiss=False)
        dismiss_button.bind(on_release=events_popup.dismiss)
        events_popup.open()

    def join_public_event(self, event, instance, classID=1):
        self.shared.nm.join_event(event, classID)


class AccountInfo(Screen):

    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)

    def update_username(self):
        self.userField.text = self.shared.username
        self.pointsField.text = str(self.shared.points)
        self.emailField.text = self.shared.email
        self.descriptionField.text = self.shared.description


class UserEvents(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)


class EventDetails(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        super(EventDetails, self).__init__(**kwargs)
        self.completed_tasks = []
        self.top_users_popup = None
        scroll_layout = ScrollView(size_hint=(1, None), size=(600, 435),
                                   pos_hint={'center_x': 0.55, 'center_y': 0.55})
        self.inside_scroll = GridLayout(cols=2, size_hint_y=None, spacing=20)
        self.inside_scroll.bind(minimum_height=self.inside_scroll.setter('height'))
        health_label = Label(text='Current Health:', size_hint=(None, None), size=(250, 40),
                             pos_hint={'center_x': 0.25, 'top': 0.1})
        health_amount = Label(size_hint=(None, None), size=(550, 40),
                              pos_hint={'center_x': 0.25, 'top': 0.1})
        event_name_label = Label(text='Event title:', size_hint=(None, None), size=(250, 40),
                                 pos_hint={'center_x': 0.25, 'top': 0.1})
        event_name = Label(size_hint=(None, None), size=(550, 40),
                           pos_hint={'center_x': 0.25, 'top': 0.1})
        shared.health_amount_label = health_amount
        shared.event_name_label = event_name
        self.inside_scroll.add_widget(health_label)
        self.inside_scroll.add_widget(health_amount)
        self.inside_scroll.add_widget(event_name_label)
        self.inside_scroll.add_widget(event_name)
        shared.event_details_scroll = self.inside_scroll
        return_main = Button(text='Main Menu',
                             size_hint=(0.15, 0.1), pos_hint={"center_x": 0.3, "top": 0.1},
                             on_release=self.switch_screen)
        display_top = Button(text='Top 5',
                             size_hint=(0.15, 0.1), pos_hint={"center_x": 0.5, "top": 0.1},
                             on_release=self.display_top_users)
        actions = Button(text='Actions',
                         size_hint=(0.15, 0.1), pos_hint={"center_x": 0.7, "top": 0.1},
                         on_release=self.display_actions)
        scroll_layout.add_widget(self.inside_scroll)
        self.add_widget(scroll_layout)
        self.add_widget(return_main)
        self.add_widget(display_top)
        self.add_widget(actions)

    def display_top_users(self, instance):
        top_users = self.shared.nm.top_five(self.shared.event_id)
        num_listed = 0
        layout = BoxLayout(orientation='vertical')
        for user in top_users[::-1]:
            num_listed += 1
            if num_listed <= 5 and user is not None:
                top_content = Label(text=f'{num_listed}: {user["username"]};  {user["points"]} points;  '
                                         f'{user["streak"]} streak;  {user["health"]} health',
                                    valign='center', halign='center')
                layout.add_widget(top_content)
        dismiss_button = Button(text='Dismiss',
                                size_hint=(None, None), size=(80, 40),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
        layout.add_widget(dismiss_button)
        self.top_users_popup = Popup(title='Top 5 Soldiers', title_align='center',
                                     content=layout,
                                     size_hint=(None, None), size=(600, 500),
                                     auto_dismiss=False)
        dismiss_button.bind(on_release=self.top_users_popup.dismiss)
        self.top_users_popup.open()
        return

    def display_actions(self, instance):
        dd = DropDown()

        def _shield(instance):
            self.process_action(self.shared.nm.client['id'], 2)
            actions_popup.dismiss()
            dd.dismiss()

        scroll_layout = ScrollView(size_hint=(1, None), size=(600, 400))
        outside_scroll = GridLayout(rows=2, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        inside_scroll = GridLayout(cols=2, size_hint_y=None, spacing=20)
        inside_scroll.bind(minimum_height=inside_scroll.setter('height'))
        dismiss_button = Button(text='Dismiss', size_hint=(None, None), size=(80, 40),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
        actions_popup = Popup(title='Actions', title_align='center',
                              content=outside_scroll,
                              size_hint=(None, None), size=(600, 500),
                              auto_dismiss=False)
        shield = Button(text='Shield', size_hint=(None, None),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        on_release=_shield)
        for participant in self.shared.nm.get_event(self.shared.event_id)['participants']:
            if participant['client'] == self.shared.nm.client['id']:
                continue
            else:
                def _attack(participant, instance):
                    self.process_action(participant['client'], 1)
                    actions_popup.dismiss()
                    dd.dismiss()

                newbtn = Button(text=f'{participant["username"]}', size_hint=(None, None), size=(80, 40),
                                on_release=partial(_attack, participant))
                dd.add_widget(newbtn)
        attack = Button(text='Attack', size_hint=(None, None),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                        on_release=dd.open)
        inside_scroll.add_widget(shield)
        inside_scroll.add_widget(attack)
        scroll_layout.add_widget(inside_scroll)
        outside_scroll.add_widget(scroll_layout)
        outside_scroll.add_widget(dismiss_button)
        dismiss_button.bind(on_release=actions_popup.dismiss)
        actions_popup.open()

    def process_action(self, target, action):
        # Action 1 is attack, 2 is shield
        self.shared.nm.take_action(self.shared.event_id, target, action)
        return

    def switch_screen(self, instance):
        self.manager.transition.direction = 'up'
        self.manager.current = 'main'

        for task in self.shared.complete:
            if task['checkbox'].state == 'normal':
                self.shared.nm.uncomplete_task(task['id'])
            else:
                pass  # Task was complete and still is
        for task in self.shared.incomplete:
            if task['checkbox'].state == 'down':
                self.shared.nm.complete_task(task['id'])
            else:
                pass  # Task was incomplete and still is


class EventCreation(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        super(EventCreation, self).__init__(**kwargs)
        self.tasks_info = []
        self.input_fields = []

        scroll_layout = ScrollView(size_hint=(1, None), size=(600, 435),
                                   pos_hint={'center_x': 0.55, 'center_y': 0.5})
        self.inside_scroll = GridLayout(cols=2, size_hint_y=None, spacing=20)
        self.inside_scroll.bind(minimum_height=self.inside_scroll.setter('height'))
        title_input_label = Label(text='Event name: ', size_hint=(None, None), size=(250, 40),
                                  pos_hint={'center_x': 0.25, 'top': 0.1})
        title_input = TextInput(size_hint=(None, None), size=(400, 40))
        self.input_fields.append(title_input)
        is_public_label = Label(text='Make event private?', size_hint=(None, None), size=(250, 40),
                                pos_hint={'center_x': 0.25, 'top': 0.1})
        is_public = CheckBox()
        date_label = Label(text='Enter due date:\n(YYYY-MM-DD format)', size_hint=(None, None), size=(250, 40),
                           pos_hint={'center_x': 0.25, 'top': 0.1})
        date_input = TextInput(size_hint=(None, None), size=(400, 40))
        self.input_fields.append(date_input)

        layout = FloatLayout(size=self.size)
        return_main = Button(text='Return to Main Menu',
                             size_hint=(0.3, 0.1), pos_hint={"center_x": 0.2, "top": 0.1},
                             on_release=self.switch_screen)
        submit_event = Button(text='Submit New Event',
                              size_hint=(0.3, 0.1), pos_hint={"center_x": 0.8, "top": 0.1},
                              on_release=partial(self.submit_event, title_input, is_public, date_input))
        new_task = Button(text='Add another task',
                          size_hint=(0.3, 0.1), pos_hint={"center_x": 0.5, "top": 0.1},
                          on_release=partial(self.add_task_box))
        self.inside_scroll.add_widget(title_input_label)
        self.inside_scroll.add_widget(title_input)
        self.inside_scroll.add_widget(is_public_label)
        self.inside_scroll.add_widget(is_public)
        self.inside_scroll.add_widget(date_label)
        self.inside_scroll.add_widget(date_input)
        scroll_layout.add_widget(self.inside_scroll)
        layout.add_widget(scroll_layout)
        layout.add_widget(submit_event)
        layout.add_widget(new_task)
        layout.add_widget(return_main)
        self.add_widget(layout)

    def submit_event(self, title_input, is_public_in, date_input, instance):
        is_public = True
        if is_public_in.state != 'normal':
            is_public = False
        event_info = self.shared.nm.create_event(title_input.text, is_public, date_input.text)
        for desc in self.tasks_info:
            name = desc.text
            self.shared.nm.create_task(name, event_info['id'])
        for field in self.input_fields:
            field.text = ''
        self.manager.transition.direction = 'left'
        self.manager.current = 'main'

    def add_task_box(self, instance):
        task_label = Label(text='Enter task description:', size_hint=(None, None), size=(250, 40),
                           pos_hint={'center_x': 0.25, 'top': 0.1})
        task_desc = TextInput(size_hint=(None, None), size=(400, 40))
        self.input_fields.append(task_desc)
        self.tasks_info.append(task_desc)
        self.inside_scroll.add_widget(task_label)
        self.inside_scroll.add_widget(task_desc)

    def switch_screen(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'main'


class PublicEventSearch(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)


class PrivateEventSearch(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        self.password = StringProperty('')
        Screen.__init__(self, **kwargs)

    def find_private_event(self, event_id):
        event_found = False
        event_results = get_all_events(self.shared)
        try:
            for event in event_results:
                if int(event_id) == event['id'] and not event['is_public']:
                    event_found = True
                    break
                else:
                    event_found = False
            if not event_found:
                popup_widget('Make sure your event ID is correct\nand try again.', 'Failed to find event')
            elif event_found:
                layout = BoxLayout(orientation='vertical')
                popup_content = Label(text=f'Event {event["name"]} found!\nPlease enter password.',
                                      valign='center', halign='center')
                password_prompt = TextInput(multiline=False, password=True)
                close_button = Button(text='Submit',
                                      size_hint=(None, None), size=(80, 40),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
                layout.add_widget(popup_content)
                layout.add_widget(password_prompt)
                layout.add_widget(close_button)
                popup = Popup(title='Event found!', title_align='center',
                              content=layout,
                              size_hint=(None, None), size=(300, 200),
                              auto_dismiss=False)
                close_button.bind(on_press=partial(self.join_private_event, event_id, password_prompt),
                                  on_release=popup.dismiss)
                popup.open()
        except ValueError:
            popup_widget('Make sure you enter an event ID\nand try again.', 'No ID entered')

    def join_private_event(self, event, password, instance, classID='1'):
        self.shared.nm.join_event(event, classID, password.text)


class RoutineHome(App):

    def __init__(self, **kwargs):
        App.__init__(self)
        self.shared = Shared()
        self.shared.app = self
        self.shared.nm = NetworkManager(self.shared)

    def build(self):
        self.title = 'Routine Royale'
        sm = ScreenManager()
        widgets = [
            RoutineLogin(shared=self.shared, name='login'),
            RoutineCreate(shared=self.shared, name='create'),
            RoutineMain(shared=self.shared, name='main'),
            AccountInfo(shared=self.shared, name='accountInfo'),
            UserEvents(shared=self.shared, name='userEvents'),
            EventCreation(shared=self.shared, name='eventCreation'),
            PublicEventSearch(shared=self.shared, name='publicEventSearch'),
            PrivateEventSearch(shared=self.shared, name='privateEventSearch'),
            EventDetails(shared=self.shared, name='eventDetails'),
        ]
        for widget in widgets:
            sm.add_widget(widget)

        self.shared.sm = sm
        self.shared.login = widgets[0]
        self.shared.create = widgets[1]
        self.shared.main = widgets[2]
        self.shared.account = widgets[3]
        self.shared.user_events = widgets[4]
        self.shared.event_create = widgets[5]
        self.shared.public_event_search = widgets[6]
        self.shared.private_event_search = widgets[7]
        self.shared.event_details = widgets[8]
        return sm


if __name__ == "__main__":
    RoutineHome().run()
