import os
import time
import json
import dataclasses
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union

from requests_oauthlib import OAuth2Session


class PymstodoError(Exception):
    pass


class Token(TypedDict):
    token_type: str
    scope: List[str]
    expires_in: int
    ext_expires_in: int
    access_token: str
    refresh_token: str
    id_token: str
    expires_at: float


class DueDate(TypedDict):
    dateTime: str
    timeZone: str


@dataclasses.dataclass
class TaskList:
    list_id: str
    displayName: str
    isOwner: bool
    isShared: bool
    wellknownListName: str

    def __init__(self, **kwargs: Union[str, bool]) -> None:
        for f in dataclasses.fields(self):
            setattr(self, f.name, kwargs.get('id' if f.name == 'list_id' else f.name))

    def __str__(self) -> str:
        return self.displayName.replace('|', '—').strip()

    @property
    def link(self) -> str:
        return 'href=https://to-do.live.com/tasks/{self.list_id}'


@dataclasses.dataclass
class Task:
    task_id: str
    title: str
    isReminderOn: bool
    importance: bool
    status: str
    createdDateTime: str
    lastModifiedDateTime: str
    dueDateTime: DueDate
    body: str

    def __init__(self, **kwargs: Union[str, int, bool]) -> None:
        for f in dataclasses.fields(self):
            setattr(self, f.name, kwargs.get('id' if f.name == 'task_id' else f.name))

    def __str__(self) -> str:
        title = self.title.replace('|', '—').strip()
        if self.due_date:
            title += f' • Due {self.due_date.strftime("%x")}'

        return title

    @property
    def created_date(self) -> Optional[datetime]:
        if self.createdDateTime:
            return datetime.strptime(self.createdDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def last_mod_date(self) -> Optional[datetime]:
        if self.lastModifiedDateTime:
            return datetime.strptime(self.lastModifiedDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def due_date(self) -> Optional[datetime]:
        if self.dueDateTime:
            return datetime.strptime(self.dueDateTime['dateTime'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None


class ToDoConnection:
    _redirect: str = 'https://localhost/login/authorized'
    _scope: str = 'openid offline_access tasks.readwrite'
    _authority: str = 'https://login.microsoftonline.com/common'
    _authorize_endpoint: str = '/oauth2/v2.0/authorize'
    _token_endpoint: str = '/oauth2/v2.0/token'
    _base_api_url: str = 'https://graph.microsoft.com/v1.0/me/todo/'

    def __init__(self, client_id: str, client_secret: str, token: Token) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token

    @classmethod
    def get_auth_url(cls, client_id: str) -> Any:
        """Get the authorization_url."""
        oa_sess = OAuth2Session(client_id, scope=cls._scope, redirect_uri=cls._redirect)

        authorize_url = f'{cls._authority}{cls._authorize_endpoint}'
        authorization_url, _ = oa_sess.authorization_url(authorize_url)

        return authorization_url

    @classmethod
    def get_token(cls, client_id: str, client_secret: str, redirect_resp: str) -> Any:
        """Fetch the access token"""
        oa_sess = OAuth2Session(client_id, scope=cls._scope, redirect_uri=cls._redirect)
        token_url = f'{cls._authority}{cls._token_endpoint}'
        token = oa_sess.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_resp)

        return token

    def _refresh_token(self) -> None:
        now = time.time()
        expire_time = self.token['expires_at'] - 300
        if now >= expire_time:
            token_url = f'{ToDoConnection._authority}{ToDoConnection._token_endpoint}'
            oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope,
                                    token=self.token, redirect_uri=ToDoConnection._redirect)
            new_token = oa_sess.refresh_token(token_url, client_id=self.client_id, client_secret=self.client_secret)
            self.token = new_token

    def get_lists(self) -> Optional[List[TaskList]]:
        """Get all task lists."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists?top=99')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())['value']
        lists = [TaskList(**list_data) for list_data in contents]

        return lists

    def create_list(self, name: str) -> Optional[TaskList]:
        """Create task list."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.post(f'{ToDoConnection._base_api_url}lists', json={'displayName': name})
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def get_list(self, list_id: str) -> Optional[TaskList]:
        """Get task list details."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists/{list_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def update_list(self, list_id: str, **list_data: Union[str, bool]) -> Optional[TaskList]:
        """Update task list details."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.patch(f'{ToDoConnection._base_api_url}lists/{list_id}', json=list_data)
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def delete_list(self, list_id: str) -> Any:
        """Delete task list."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.delete(f'{ToDoConnection._base_api_url}lists/{list_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        return resp.ok

    def get_tasks(self, list_id: str) -> Optional[List[Task]]:
        """Get all uncompleted tasks for the list."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f"{ToDoConnection._base_api_url}lists/{list_id}/tasks?top=99&$filter=status ne 'completed'")
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())['value']
        tasks = [Task(**task_data) for task_data in contents]

        return tasks

    def create_task(self, title: str, list_id: str, due_date: Optional[datetime] = None) -> Optional[Task]:
        """Create task in the list."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        task_data: Dict[str, Any] = {'title': title}
        if due_date:
            task_data['dueDateTime'] = {'dateTime': due_date.strftime('%Y-%m-%dT%H:%M:%S.0000000'), 'timeZone': 'UTC'}
        resp = oa_sess.post(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks', json=task_data)
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def get_task(self, task_id: str, list_id: str) -> Optional[Task]:
        """Get task details."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def update_task(self, task_id: str, list_id: str, **task_data: Union[str, int, bool]) -> Optional[Task]:
        """Update task details."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.patch(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}', json=task_data)
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def delete_task(self, task_id: str, list_id: str) -> bool:
        """Delete task from list."""
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.delete(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        return True

    def complete_task(self, task_id: str, list_id: str) -> Optional[Task]:
        """Complete task from list."""
        return self.update_task(task_id, list_id, status='completed')


os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'
