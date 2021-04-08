import kivy

from network import NetworkManager

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from shared import Shared


class RoutineLogin(Screen):

    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)

    def LoginAccount(self, userInput, password):
        logged_in = self.shared.nm.login(userInput, password)
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


class EventCreation(Screen):
    pass


class EventSearch(Screen):
    pass

    def list_public_events(self):
        events = self.shared.nm.get('/events/', True)
        for event in events['results']:
            if event['is_public']:
                self.public_event_widget(event)
            print(event)

    def public_event_widget(self, event):
        print(event['id'])
        w = Widget
        return

    def join_public_event(self, eventID, classID=1):
        return


class PrivateEventSearch(Screen):
    def __init__(self, shared: Shared, **kwargs):
        self.shared = shared
        Screen.__init__(self, **kwargs)

    def find_private_event(self, event_id):
        print(event_id)
        return


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
            PrivateEventSearch(shared=self.shared, name='privateEventSearch')
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
        return sm


if __name__ == "__main__":
    RoutineHome().run()
