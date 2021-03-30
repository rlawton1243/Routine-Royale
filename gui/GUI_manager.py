import kivy
import requests

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


class RoutineLogin(Screen):
    pass


class RoutineCreate(Screen):
    pass

    def CreateAccount(self, username, password):
        s = login()
        if 'csrftoken' in s.cookies:
            # Django 1.6 and up
            csrftoken = s.cookies['csrftoken']
        else:
            # older versions
            csrftoken = s.cookies['csrf']
        userID = addUser(username, password, csrftoken, s)
        addClient(userID, csrftoken, s)
        return


class RoutineMain(Screen):
    pass


class RoutineHome(App):

    def build(self):
        self.title = 'Routine Royale!'
        sm = ScreenManager()
        sm.add_widget(RoutineLogin(name='login'))
        sm.add_widget(RoutineCreate(name='create'))
        return sm


# TODO: Make this all a new class for Network interaction


def _url(path):
    return 'http://127.0.0.1:8000' + path


def addClient(userID, csrftoken, s, points=0, desc='placeholder'):
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


def addUser(username, password, csrftoken, s):
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


def login():
    with requests.Session() as s:
        s.get('http://127.0.0.1:8000/api-auth/login/')
        if 'csrftoken' in s.cookies:
            # Django 1.6 and up
            csrftoken = s.cookies['csrftoken']
        else:
            # older versions
            csrftoken = s.cookies['csrf']
        payload = {
            'username': 'ryan',
            'password': '1234',
            'csrfmiddlewaretoken': csrftoken,
            'next': '/'
        }

        p = s.post('http://127.0.0.1:8000/api-auth/login/', data=payload)
        return s


if __name__ == "__main__":
    RoutineHome().run()
