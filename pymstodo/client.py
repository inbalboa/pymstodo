import os
import time
import json
import dataclasses
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

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


class _DueDate(TypedDict):
    dateTime: str
    timeZone: str


class _Body(TypedDict):
    content: str
    contentType: Literal['text', 'html']


@dataclasses.dataclass
class TaskList:
    '''
    **To-Do task list** contains one or more todoTask resources.
    '''

    list_id: str
    '''The identifier of the task list, unique in the user's mailbox. Read-only.'''

    displayName: str
    '''The name of the task list.'''

    isOwner: bool
    '''`True` if the user is owner of the given task list.'''

    isShared: bool
    '''`True` if the task list is shared with other users.'''

    wellknownListName: Literal['none', 'defaultList', 'flaggedEmails', 'unknownFutureValue']
    '''Property indicating the list name if the given list is a well-known list. Possible values are: `none`, `defaultList`, `flaggedEmails`, `unknownFutureValue`.'''

    def __init__(self, **kwargs: Any) -> None:
        for f in dataclasses.fields(self):
            setattr(self, f.name, kwargs.get('id' if f.name == 'list_id' else f.name))

    def __str__(self) -> str:
        return self.displayName.replace('|', '—').strip()

    @property
    def link(self) -> str:
        return 'href=https://to-do.live.com/tasks/{self.list_id}'


@dataclasses.dataclass
class Task:
    '''
    **To-Do task** represents a task, such as a piece of work or personal item, that can be tracked and completed.
    '''

    task_id: str
    '''Unique identifier for the task. By default, this value changes when the item is moved from one list to another.'''

    body: _Body

    categories: list[str]
    '''The categories associated with the task.'''

    completedDateTime: str
    createdDateTime: str
    dueDateTime: _DueDate

    hasAttachments: bool
    '''Indicates whether the task has attachments.'''

    title: str
    '''A brief description of the task.'''

    importance: Literal['low', 'normal', 'high']
    '''The importance of the task. Possible values are: `low`, `normal`, `high`.'''

    isReminderOn: bool
    '''Set to true if an alert is set to remind the user of the task.'''

    lastModifiedDateTime: str
    reminderDateTime: str
    startDateTime: str

    status: Literal['notStarted', 'inProgress', 'completed', 'waitingOnOthers', 'deferred']
    '''Indicates the state or progress of the task. Possible values are: `notStarted`, `inProgress`, `completed`, `waitingOnOthers`, `deferred`.'''

    def __init__(self, **kwargs: Any) -> None:
        for f in dataclasses.fields(self):
            setattr(self, f.name, kwargs.get('id' if f.name == 'task_id' else f.name))

    def __str__(self) -> str:
        title = self.title.replace('|', '—').strip()
        if self.due_date:
            title += f' • Due {self.due_date.strftime("%x")}'

        return title

    @property
    def body_text(self) -> Optional[str]:
        '''The task body that typically contains information about the task.'''
        if self.body:
            return self.body['content']
        else:
            return None

    @property
    def completed_date(self) -> Optional[datetime]:
        '''The date and time in the specified time zone that the task was finished.'''
        if self.completedDateTime:
            return datetime.strptime(self.completedDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def created_date(self) -> Optional[datetime]:
        '''The date and time when the task was created. It is in UTC.'''
        if self.createdDateTime:
            return datetime.strptime(self.createdDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def due_date(self) -> Optional[datetime]:
        '''The date and time in the specified time zone that the task is to be finished.'''
        if self.dueDateTime:
            return datetime.strptime(self.dueDateTime['dateTime'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def last_mod_date(self) -> Optional[datetime]:
        '''The date and time when the task was last modified. It is in UTC.'''
        if self.lastModifiedDateTime:
            return datetime.strptime(self.lastModifiedDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def reminder_date(self) -> Optional[datetime]:
        '''The date and time in the specified time zone for a reminder alert of the task to occur.'''
        if self.reminderDateTime:
            return datetime.strptime(self.reminderDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    @property
    def start_date(self) -> Optional[datetime]:
        '''The date and time in the specified time zone at which the task is scheduled to start.    '''
        if self.startDateTime:
            return datetime.strptime(self.startDateTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            return None


class ToDoConnection:
    '''**To-Do connection**
    your entry point to To-Do API
    '''
    _redirect: str = 'https://localhost/login/authorized'
    _scope: str = 'openid offline_access tasks.readwrite'
    _authority: str = 'https://login.microsoftonline.com/common'
    _authorize_endpoint: str = '/oauth2/v2.0/authorize'
    _token_endpoint: str = '/oauth2/v2.0/token'
    _base_api_url: str = 'https://graph.microsoft.com/v1.0/me/todo/'

    def __init__(self, client_id: str, client_secret: str, token: Token) -> None:
        self.client_id: str = client_id
        '''API client ID.'''

        self.client_secret: str = client_secret
        '''API client secret.'''

        self.token: Token = token
        '''Token obtained by method `get_token`.'''

    @staticmethod
    def get_auth_url(client_id: str) -> Any:
        '''Get the authorization_url.
    
        Args:
            client_id: API client ID

        Returns:
            Authorization URL to show to the user.
        '''
        oa_sess = OAuth2Session(client_id, scope=ToDoConnection._scope, redirect_uri=ToDoConnection._redirect)

        authorize_url = f'{ToDoConnection._authority}{ToDoConnection._authorize_endpoint}'
        authorization_url, _ = oa_sess.authorization_url(authorize_url)

        return authorization_url

    @staticmethod
    def get_token(client_id: str, client_secret: str, redirect_resp: str) -> Any:
        '''Fetch the access token.'''
        oa_sess = OAuth2Session(client_id, scope=ToDoConnection._scope, redirect_uri=ToDoConnection._redirect)
        token_url = f'{ToDoConnection._authority}{ToDoConnection._token_endpoint}'
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

    def get_lists(self, limit: Optional[int] = 99) -> Optional[List[TaskList]]:
        '''Get a list of the task lists.

        Args:
            limit: *optional* The limit size of the response (default is `99`)

        Returns:
            A list of the task lists.

        Raises:
            `PymstodoError`: An error occurred accessing the API.
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists?$top={limit}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())['value']
        lists = [TaskList(**list_data) for list_data in contents]

        return lists

    def create_list(self, name: str) -> Optional[TaskList]:
        '''Create a new task list.

        Args:
            name: Title of the new task list

        Returns:
            A created task list.

        Raises:
            `PymstodoError`: An error occurred accessing the API.
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.post(f'{ToDoConnection._base_api_url}lists', json={'displayName': name})
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def get_list(self, list_id: str) -> Optional[TaskList]:
        '''Read the properties of a task list.

        Args:
            list_id: Unique identifier for the task list

        Returns:
            A task list object.

        Raises:
            `PymstodoError`: An error occurred accessing the API.
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists/{list_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def update_list(self, list_id: str, **list_data: Union[str, bool]) -> Optional[TaskList]:
        '''Update the properties of a task list.

        Args:
            list_id: Unique identifier for the task list
            list_data: Task properties from `TaskList` object

        Returns:
            An updated task list.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.patch(f'{ToDoConnection._base_api_url}lists/{list_id}', json=list_data)
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def delete_list(self, list_id: str) -> bool:
        '''Delete a task list.

        Args:
            list_id: Unique identifier for the task list

        Returns:
            `True`: If success.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.delete(f'{ToDoConnection._base_api_url}lists/{list_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        return True

    def get_tasks(self, list_id: str, limit: Optional[int] = 0, status: Optional[Literal['notStarted', 'inProgress', 'completed', 'waitingOnOthers', 'deferred']] = None) -> List[Task]:
        '''Get tasks by a specified task list.

        Args:
            list_id: Unique identifier for the task list
            limit: *optional* The limit size of the response (default is `1000`)
            status: *optional* The state or progress of the task. Possible values are: `notStarted`, `inProgress`, `completed`, `waitingOnOthers`, `deferred` (default is `notCompleted`)

        Returns:
            Tasks of a specified task list.

        Raises:
            `PymstodoError`: An error occurred accessing the API.
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        filters = {
            'completed': "filter=status eq 'completed'",
            'notCompleted': "filter=status ne 'completed'",
            'all': None
        }
        eff_limit = limit or 1000
        default_status = 'notCompleted'
        params = (
            filters.get(status or default_status, filters[default_status]),
            f'top={eff_limit}'
        )
        params_str = '&$'.join(filter(None, params))
        url = f"{ToDoConnection._base_api_url}lists/{list_id}/tasks?${params_str}"
        contents: List[Dict[str, Any]] = []
        while (len(contents) < eff_limit or eff_limit <= 0) and url:
            resp = oa_sess.get(url)
            if not resp.ok:
                raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')
            resp_content = json.loads(resp.content.decode())
            url = resp_content.get('@odata.nextLink')
            contents.extend(resp_content['value'])
        if limit:
            contents = contents[:limit]
        tasks = [Task(**task_data) for task_data in contents]

        return tasks

    def create_task(self, title: str, list_id: str, due_date: Optional[datetime] = None, body_text: Optional[str] = None) -> Task:
        '''Create a new task in a specified task list.

        Args:
            title: A brief description of the task
            list_id: Unique identifier for the task list
            due_date: *optional* The date and time that the task is to be finished
            body_text: *optional* Information about the task

        Returns:
            A created task.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        task_data: Dict[str, Any] = {'title': title}
        if due_date:
            task_data['dueDateTime'] = {'dateTime': due_date.strftime('%Y-%m-%dT%H:%M:%S.0000000'), 'timeZone': 'UTC'}
        if body_text:
            task_data['body'] = {'content': body_text, 'contentType': 'text'}
        resp = oa_sess.post(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks', json=task_data)
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def get_task(self, task_id: str, list_id: str) -> Task:
        '''Read the properties of a task.

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list

        Returns:
            A task object.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def update_task(self, task_id: str, list_id: str, **task_data: Union[str, int, bool]) -> Task:
        '''Update the properties of a task.

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list
            task_data: Task properties from `Task` object

        Returns:
            An updated task.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.patch(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}', json=task_data)
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def delete_task(self, task_id: str, list_id: str) -> bool:
        '''Delete a task.

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list

        Returns:
            `True`: If success.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.delete(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}')
        if not resp.ok:
            raise PymstodoError(f'Error {resp.status_code}: {resp.reason}')

        return True

    def complete_task(self, task_id: str, list_id: str) -> Task:
        '''Complete a task.

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list

        Returns:
            A completed task.

        Raises:
            `PymstodoError`: An error occurred accessing the API.'''
        return self.update_task(task_id, list_id, status='completed')


#os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
#os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'
