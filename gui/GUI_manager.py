import kivy
import requests
import json

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

SERVICE_URL = 'http://127.0.0.1:8000'
_url = lambda ext: SERVICE_URL + ext


class RoutineLogin(Screen):

    def LoginAccount(self, username, password):
        self.manager.session.login(username, password)
        print(self.manager.session.get_values('/events/', []))
        self.manager.current = 'main'


class RoutineCreate(Screen):

    def CreateAccount(self, username, password):
        userID = self.manager.session.add_user(username, password, self.manager.session.csrftoken)
        self.s.add_client(userID, self.manager.session.csrftoken)


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
class NetworkManager:

    def __init__(self):
        self.s = None
        self.logged_in = False

    @property
    def csrf(self):
        """
        Gets changing CSRF token from session.
        :return: Current CSRF token
        """
        return self.s.cookies['csrftoken']

    def post(self, url, payload):
        """
        POSTs using the connection appending CSRF if exists
        :param url: str URL to POST to
        :param payload: Dictionary
        :return: Response
        """
        headers = {
                'X-CSRFToken': self.csrf,
                'Referer':     '/'
        }
        return self.s.post(_url(url), data=payload, headers=headers)

    def get(self, url, json_decode=False):
        """
        GETs using current connection.
        :param url: str URL to GET
        :param json_decode: Decode JSON
        :return: Response
        """
        if not json_decode:
            return self.s.get(_url(url))
        else:
            response = self.get(url)
            if 200 <= response.status_code <= 299:
                try:
                    return json.loads(response.content)
                except Exception as e:
                    raise IOError(f"Invalid JSON {response.content} ({response.status_code})  ({e})")
            else:
                raise IOError(f"GET response was unexpected at {url}: {response.status_code} : {response.content}")

    def get_values(self, url, values: list):
        """
        GETS using current connection, looking for specific variables.
        :param url: str URL to GET
        :param values: List of Variables to fetch
        :return: Dictionary of Requested Variables (if found, else None)
        """
        response = self.get(url, json_decode=True)
        response: dict
        result = {}
        for item in values:
            if item in response.keys():
                result[item] = response[item]
        return result

    def login(self, username, password):
        login_session = requests.Session()
        self.s = login_session
        login_session.get('http://127.0.0.1:8000/api-auth/login/')

        payload = {
                'username': username,
                'password': password,
        }

        self.post("/api-auth/login/", payload)

        response = self.get('/test_login/')
        if response.status_code == 200:
            self.logged_in = True
        else:
            self.logged_in = False
            print(f"Error Logging in: {response.status_code} {response.content}")

    def add_client(self, userID, points=0, desc='placeholder'):
        payload = {
                'user':             {userID},
                'user_points':      points,
                'user_description': desc,
        }

        return self.post('/clients/', payload)

    def add_user(self, username, password):
        payload = {
                'username': username.text,
                'password': password.text,
        }

        return self.post('/users', payload)['id']

    def join_event(self, event_id, class_id):
        """
        Joins authenticated user to an Event using API call
        :param event_id: PK for Event to join
        :param class_id: PK for selected class (User must own)
        :return: None
        """
        payload = {
                'event': event_id,
                'class': class_id,
        }
        response = self.post('/events/join_user/', payload)
        print(response)


if __name__ == "__main__":
    RoutineHome().run()
