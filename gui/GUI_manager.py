import kivy
import requests

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


class RoutineLogin(Screen):
    pass

    def LoginAccount(self, username, password):
        return


class RoutineCreate(Screen):
    pass

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

    def build(self):
        self.title = 'Routine Royale!'
        sm = ScreenManager()
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

    def addClient(self, userID, csrftoken, s, points=0, desc='placeholder'):
        headers = {
            'X-CSRFToken': csrftoken,
            'Referer': '/'
        }
        r = s.post(_url('/clients/'), data={
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
        x = s.post(_url('/users/'), data={
            'username': username.text,
            'password': password.text,
            'next': '/'
        }, headers=headers)
        return x.json()['id']

    def login(self):
        with requests.Session() as s:
            self.s.get('http://127.0.0.1:8000/api-auth/login/')
            if 'csrftoken' in s.cookies:
                # Django 1.6 and up
                self.csrftoken = s.cookies['csrftoken']
            else:
                # older versions
                self.csrftoken = s.cookies['csrf']
            payload = {
                'username': 'ryan',
                'password': '1234',
                'csrfmiddlewaretoken': self.csrftoken,
                'next': '/'
            }

            s.post(_url("/api-auth/login/"), data=payload)
            return s


if __name__ == "__main__":
    RoutineHome().run()
