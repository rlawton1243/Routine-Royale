import kivy
import requests

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget


# TODO: Remove all test prints, convert to .kv instead

class RoutineLogin(Widget):
    pass
    # def __init__(self, **kwargs):
    #    super(RoutineLogin, self).__init__(**kwargs)
    #    self.cols = 2
    #    self.add_widget(Label(text='User Name: '))
    #    self.username = TextInput(multiline=False)
    #    self.add_widget(self.username)
    #    self.add_widget(Label(text='Password: '))
    #    self.password = TextInput(password=True, multiline=False)
    #    self.add_widget(self.password)
    #    self.createAccount = (Button(text='Create New Account'))
    #    self.createAccount.bind(on_press=self.CreatePress)
    #    self.add_widget(self.createAccount)
    #    self.loginButton = (Button(text='Login'))
    #    self.loginButton.bind(on_press=self.LoginPress)
    #    self.add_widget(self.loginButton)

    # def LoginPress(self, instance):
    #    print('login button test')
    #    print(self.username.text)
    #    print(self.password.text)
    #    return

    # def CreatePress(self, instance):
    #    return RoutineCreate()


class RoutineCreate(GridLayout):

    def __init__(self, **kwargs):
        super(RoutineCreate, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='User Name: '))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='Password: '))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)
        self.createAccount = (Button(text='Return to login'))
        self.createAccount.bind(on_press=self.ReturnLogin)
        self.add_widget(self.createAccount)
        self.loginButton = (Button(text='Create Account'))
        self.loginButton.bind(on_press=self.CreateAccount)
        self.add_widget(self.loginButton)

    def ReturnLogin(self, instance):
        # TODO: Remove test prints
        print('Return test')
        return

    def CreateAccount(self, instance):
        # TODO: Remove test prints
        print('Create account test')
        print(self.username.text)
        print(self.password.text)
        s = login()
        if 'csrftoken' in s.cookies:
            # Django 1.6 and up
            csrftoken = s.cookies['csrftoken']
        else:
            # older versions
            csrftoken = s.cookies['csrf']
        userID = addUser(self.username, self.password, csrftoken, s)
        addClient(userID, csrftoken, s)
        return


class RoutineHome(App):

    def build(self):
        return RoutineCreate()


# TODO : Make this all a new class for Network interaction


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
    print(r)
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
        print(s.cookies)
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
        print(p.text)
        return s


if __name__ == "__main__":
    RoutineHome().run()
