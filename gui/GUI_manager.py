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

    def CreateAccount(self, username, password):
        userID = self.manager.session.add_user(username, password, self.manager.session.csrftoken)
        self.s.add_client(userID, self.manager.session.csrftoken)


class RoutineMain(Screen):
    pass


class AccountInfo(Screen):

    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)

    def update_username(self):
        self.userField.text = self.shared.username


class UserEvents(Screen):
    pass


class EventDetails(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        super(EventDetails, self).__init__(**kwargs)
        self.completed_tasks = []

        scroll_layout = ScrollView(size_hint=(1, None), size=(600, 435),
                                   pos_hint={'center_x': 0.55, 'center_y': 0.5})
        self.inside_scroll = GridLayout(cols=2, size_hint_y=None, spacing=20)
        self.inside_scroll.bind(minimum_height=self.inside_scroll.setter('height'))
        event_name_label = Label(text='Event title:')
        event_name = Label(text=f'{self.shared.req_event_title}')
        self.inside_scroll.add_widget(event_name_label)
        self.inside_scroll.add_widget(event_name)
        for task in self.shared.req_event_tasks:
            task_desc = Label(text=f'{task}; complete?')
            task_comp = CheckBox()
            self.completed_tasks.append(task_comp)
            self.inside_scroll.add_widget(task_desc)
            self.inside_scroll.add_widget(task_comp)
        return_main = Button(text='Return to Main Menu',
                             size_hint=(0.3, 0.1), pos_hint={"center_x": 0.5, "top": 0.1},
                             on_release=self.switch_screen)
        scroll_layout.add_widget(self.inside_scroll)
        self.add_widget(scroll_layout)
        self.add_widget(return_main)

    def switch_screen(self, instance):
        self.manager.transition.direction = 'up'
        self.manager.current = 'userEvents'


class EventCreation(Screen):
    pass


class EventSearch(Screen):
    pass

    def list_public_events(self):
        event_results = self.get_all_events()
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
                end_date_label = Label(text=f'\nEnd date info:\nMonth: {final_end_date[1]} Day: {final_end_date[2]}\n'
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
        events_popup = Popup(title='Public Events', title_align='center',
                             content=outside_scroll,
                             size_hint=(None, None), size=(600, 500),
                             auto_dismiss=False)
        dismiss_button.bind(on_release=events_popup.dismiss)
        events_popup.open()

    def join_public_event(self, event, instance, classID=1):
        self.shared.nm.join_event(event, classID)


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
