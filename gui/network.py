import json

import requests

from shared import Shared

SERVICE_URL = 'http://127.0.0.1:8000'
_url = lambda ext: SERVICE_URL + ext


# TODO: Finalize NetworkManager
class NetworkManager:

    def __init__(self, shared: Shared):
        self.s = requests.Session()
        self.logged_in = False
        self.userID = None
        self.shared = shared

    @property
    def csrf(self):
        """
        Gets changing CSRF token from session.
        :return: Current CSRF token
        """
        if self.s.cookies is not None and 'csrftoken' in self.s.cookies:
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
            'Referer': '/'
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
        GETs using current connection, looking for specific variables.
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
        self.s.get(_url('/api-auth/login/'))

        payload = {
            'username': username,
            'password': password,
        }

        self.post("/api-auth/login/", payload)

        response = self.get('/test_login/')
        if response.status_code == 200:
            self.logged_in = True
            self.userID = response.json()['user']
            self.shared.username = self.get(f'/users/{self.userID}', json_decode=True)['username']
        else:
            self.logged_in = False
            print(f"Error Logging in: {response.status_code} {response.content}")
        return self.logged_in

    def add_client(self, userID, points=0, desc='placeholder'):
        payload = {
            'user': {userID},
            'user_points': points,
            'user_description': desc,
        }

        self.post('/clients/', payload)

    def add_user(self, username, password):
        payload = {
            'username': username.text,
            'password': password.text,
        }

        res = self.post('/users/', payload)
        if res.status_code > 299:
            raise IOError(f"Username and Password not accepted: {res.json()}")
        return res.json()['id']

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
