import datetime
import json

import requestsimport

datetime

datetime

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

    def post(self, url, payload, json_decode=False, json_encode=False):
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
        if not json_encode:
            response = self.s.post(_url(url), data=payload, headers=headers)
        else:
            response = self.s.post(_url(url), json=payload, headers=headers)
        if not json_decode:
            return response
        else:
            if 200 <= response.status_code <= 299:
                try:
                    return json.loads(response.content)
                except Exception as e:
                    raise IOError(f"Invalid JSON {response.content} ({response.status_code})  ({e})")
            else:
                raise IOError(f"GET response was unexpected at {url}: {response.status_code} : {response.content}")

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

    def change_password(self, new_password):
        """
        Changes the password for the logged in user.
        :param new_password: str New Password
        :return: None
        """
        assert self.logged_in, "Log in to change password."
        payload = {
                'password': new_password
        }
        response = self.post('/clients/change_password/', payload)
        if response.status_code > 299:
            print(response.content)

    def change_email(self, new_email):
        """
        Changes the password for the logged in user.
        :param new_email: str New Email
        :return: None
        """
        assert self.logged_in, "Log in to change password."
        payload = {
                'password': new_email
        }
        response = self.post('/clients/change_email/', payload)
        if response.status_code > 299:
            print(response.content)

    def add_client(self, userID, points=0, desc='placeholder'):
        payload = {
                'user':             {userID},
                'user_points':      points,
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
            print(res.content)
            raise IOError(f"Username and Password not accepted: {res.json()}")
        return res.json()['id']

    def join_event(self, event_id, class_id, private_key=None):
        """
        Joins authenticated user to an Event using API call
        :param event_id: PK for Event to join
        :param class_id: PK for selected class (User must own)
        :param private_key: int If Private Event, pass the key
        :return: None
        """
        payload = {
            'event': event_id,
            'class': class_id,
        }
        if private_key is not None:
            payload['key'] = f"{event_id}-{private_key}"
        response = self.post('/events/join_user/', payload)
        if response.status_code > 299:
            print(response.content)

    def top_five(self, event_id):
        assert self.logged_in, "Log in to see Top 5."
        payload = {
                'event': event_id
        }
        response = self.post('/events/top_five/', payload, json_decode=True)
        return response

    def get_event_tasks(self, event_id):
        """
        Returns tasks of Event as a list of complete and a list of incomplete Tasks
        :param event_id: int Event PK
        :return: complete, incomplete
        """
        assert self.logged_in, "Log in to see remaining Event tasks."
        payload = {
                'event': event_id
        }
        all = self.post('/tasks/all_event/', payload, json_decode=True)
        incomplete = self.post('/tasks/remaining_event/', payload, json_decode=True)
        complete = []
        for task in all:
            found = False
            for inc in incomplete:
                if inc['id'] == task['id']:
                    found = True
            if not found:
                complete.append(task)

        return complete, incomplete

    def complete_task(self, task_id):
        """
        Marks task as Completed.
        :param task_id: PK to Task
        :return: None
        """
        print(f"Completing {task_id}")
        assert self.logged_in, "Log in to complete a Task."
        payload = {
                'task': task_id
        }
        response = self.post('/tasks/complete/', payload)
        if response.status_code > 299:
            print(response.content)

    def uncomplete_task(self, task_id):
        """
        Marks task as NOT Completed.
        :param task_id: PK to Task
        :return: None
        """
        print(f"Uncompleting {task_id}")
        assert self.logged_in, "Log in to uncomplete a Task."
        payload = {
            'task': task_id
        }
        response = self.post('/tasks/uncomplete/', payload)
        if response.status_code > 299:
            print(response.content)

    def create_event(self, name, is_public=True):
        assert self.logged_in, "Log in to create an event."
        payload = {
            'name': name,
            'is_public': is_public
        }
        response = self.post('/events/', payload)
        if response.status_code > 299:
            print(response.content)
        return json.loads(response.content)

    def create_task(self, name, event, repeating=False, schedule=None, due_time=None):
        payload = {
            'name': name,
            'event': event,
            'repeating': repeating,
        }
        if schedule is not None:
            payload['schedule'] = schedule
        if due_time is not None:
            payload['due_time'] = due_time
        else:
            payload['due_time'] = datetime.datetime.today().replace(hour=11, minute=59, second=59)

        response = self.post('/tasks/', payload)
        if response.status_code > 299:
            print(response.content)
        return json.loads(response.content)
