import kivy
import requests

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


class RoutineLogin(Screen):

    def LoginAccount(self, username, password):
        self.manager.session.login(username, password)
        self.manager.session.join_event()
        self.manager.current = 'main'


class RoutineCreate(Screen):

    def CreateAccount(self, username, password):
        userID = self.manager.session.addUser(username, password, self.manager.session.csrftoken)
        self.s.addClient(userID, self.manager.session.csrftoken)


class RoutineMain(Screen):
    pass


class AccountInfo(Screen):
    pass


class UserEvents(Screen):
    pass


class EventCreation(Screen):
    pass


class EventSearch(Screen):
    pass

    def SearchDB(self):
        return


class RoutineHome(App):

    def __init__(self, **kwargs):
        App.__init__(self)

    def build(self):
        self.title = 'Routine Royale'
        sm = ScreenManager()
        sm.session = NetworkManager()
        sm.add_widget(RoutineLogin(name='login'))
        sm.add_widget(RoutineCreate(name='create'))
        sm.add_widget(RoutineMain(name='main'))
        sm.add_widget(AccountInfo(name='accountInfo'))
        sm.add_widget(UserEvents(name='userEvents'))
        sm.add_widget(EventCreation(name='eventCreation'))
        sm.add_widget(EventSearch(name='eventSearch'))
        return sm


# TODO: Finalize NetworkManager

def _url(path):
    return 'http://127.0.0.1:8000' + path


class NetworkManager:

    def __init__(self):
        self.s = None
        self.csrftoken = None
        self.cookies = None
        self.logged_in = False

    def post(self, url, payload):
        """
        POSTs using the connection appending CSRF if exists
        :param url: str URL to POST to
        :param payload: Dictionary
        :return: Response
        """
        if self.csrftoken:
            payload['csrfmiddlewaretoken'] = self.csrftoken
        return self.s.post(_url(url), data=payload)

    def addClient(self, userID, csrftoken, points=0, desc='placeholder'):
        headers = {
            'X-CSRFToken': csrftoken,
            'Referer': '/'
        }
        r = self.s.post(_url('/clients/'), data={
            'user': f'{_url("/users/")}{userID}/',
            'user_points': points,
            'user_description': desc,
            'next': '/'
        }, headers=headers)
        return r

    def addUser(self, username, password, csrftoken):
        headers = {
            'X-CSRFToken': csrftoken,
            'Referer': '/'
        }
        x = self.s.post(_url('/users/'), data={
            'username': username.text,
            'password': password.text,
            'next': '/'
        }, headers=headers)
        return x.json()['id']

    def login(self, username, password):
        with requests.Session() as login_session:
            login_session.get('http://127.0.0.1:8000/api-auth/login/')
            if 'csrftoken' in login_session.cookies:
                # Django 1.6 and up
                self.csrftoken = login_session.cookies['csrftoken']
            else:
                # older versions
                self.csrftoken = login_session.cookies['csrf']
            payload = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': self.csrftoken,
                'next': '/'
            }

            response = login_session.post(_url("/api-auth/login/"), data=payload)
            # print(response)
            self.s = login_session
            self.logged_in = True

    def join_event(self, event_id=1, class_id=1):
        """
        Joins authenticated user to an Event using API call
        :param event_id: PK for Event to join
        :param class_id: PK for selected class (User must own)
        :return: None
        """
        payload = {
            'event': event_id,
            'class': class_id,
            'csrfmiddlewaretoken': self.csrftoken,
            'next': '/'
        }
        response = self.s.post(_url('/events/join_user/'), data=payload)
        print(response)


if __name__ == "__main__":
    RoutineHome().run()
