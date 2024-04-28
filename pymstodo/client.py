import dataclasses
import json
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, TypedDict
from zoneinfo import ZoneInfo

from requests_oauthlib import OAuth2Session

from .windows_zones_adapter import get_zoneinfo_name_by_windows_zone


class PymstodoError(Exception):
    '''Basic Pymstodo exception'''

    def __init__(self, status_code: int, reason: str):
        super().__init__(f'Error {status_code}: {reason}')


class Token(TypedDict):
    token_type: str
    scope: list[str]
    expires_in: int
    ext_expires_in: int
    access_token: str
    refresh_token: str
    id_token: str
    expires_at: float


class _DateTimeTimeZone(TypedDict):
    dateTime: str
    timeZone: str


class _Body(TypedDict):
    content: str
    contentType: Literal['text', 'html']


class WellknownListName(Enum):
    '''
    Well-known list name

    Attributes:
        DEFAULT_LIST: Default list
        FLAGGED_EMAILS: Flagged emails
        UNKNOWN_FUTURE_VALUE: Unknown future value
    '''

    DEFAULT_LIST = 'defaultList'
    FLAGGED_EMAILS = 'flaggedEmails'
    UNKNOWN_FUTURE_VALUE = 'unknownFutureValue'


class TaskStatus(Enum):
    '''
    The state or progress of the task

    Attributes:
        notStarted: not started
        inProgress: in progress
        completed: completed
        waitingOnOthers: waiting on others
        deferred: deferred
    '''

    NOT_STARTED = 'notStarted'
    IN_PROGRESS = 'inProgress'
    COMPLETED = 'completed'
    WAITING_ON_OTHERS = 'waitingOnOthers'
    DEFERRED = 'deferred'


class TaskStatusFilter(Enum):
    '''
    Tasks status filter

    Attributes:
        completed: only completed tasks
        notCompleted: only non-completed tasks
        all: all tasks
    '''

    COMPLETED = 'completed'
    NOT_COMPLETED = 'notCompleted'
    ALL = 'all'


@dataclasses.dataclass
class TaskList:
    '''**To-Do task list** contains one or more task'''

    list_id: str
    '''The identifier of the task list, unique in the user's mailbox. Read-only'''

    displayName: str
    '''The name of the task list'''

    isOwner: bool
    '''`True` if the user is owner of the given task list'''

    isShared: bool
    '''`True` if the task list is shared with other users'''

    wellknownListName: str

    def __init__(self, **kwargs: Any) -> None:
        for f in dataclasses.fields(self):
            setattr(self, f.name, kwargs.get('id' if f.name == 'list_id' else f.name))

    def __str__(self) -> str:
        return self.displayName.replace('|', '—').strip()

    @property
    def link(self) -> str:
        '''Link to the task list on web.'''
        return 'href=https://to-do.live.com/tasks/{self.list_id}'

    @property
    def wellknown_list_name(self) -> WellknownListName | None:
        '''Property indicating the list name if the given list is a well-known list'''
        return None if self.wellknownListName == 'none' else WellknownListName(self.wellknownListName)


@dataclasses.dataclass
class Task:
    '''**To-Do task** represents a task, such as a piece of work or personal item, that can be tracked and completed'''

    task_id: str
    '''Unique identifier for the task. By default, this value changes when the item is moved from one list to another'''

    body: _Body

    categories: list[str]
    '''The categories associated with the task'''

    completedDateTime: _DateTimeTimeZone
    '''The date and time in the specified time zone that the task was finished. Uses ISO 8601 format'''

    createdDateTime: str
    '''The date and time when the task was created. It is in UTC and uses ISO 8601 format'''

    dueDateTime: _DateTimeTimeZone
    '''The date and time in the specified time zone that the task is to be finished. Uses ISO 8601 format'''

    hasAttachments: bool
    '''Indicates whether the task has attachments'''

    title: str
    '''A brief description of the task'''

    importance: Literal['low', 'normal', 'high']
    '''The importance of the task. Possible values are: `low`, `normal`, `high`'''

    isReminderOn: bool
    '''Set to true if an alert is set to remind the user of the task'''

    lastModifiedDateTime: str
    '''The date and time when the task was last modified. It is in UTC and uses ISO 8601 format'''

    reminderDateTime: _DateTimeTimeZone
    '''The date and time in the specified time zone for a reminder alert of the task to occur. Uses ISO 8601 format'''

    startDateTime: _DateTimeTimeZone
    '''The date and time in the specified time zone at which the task is scheduled to start. Uses ISO 8601 format'''

    status: str

    def __init__(self, **kwargs: Any) -> None:
        for f in dataclasses.fields(self):
            setattr(self, f.name, kwargs.get('id' if f.name == 'task_id' else f.name))

    def __str__(self) -> str:
        title = self.title.replace('|', '—').strip()
        if self.due_date:
            title += f' • Due {self.due_date.strftime("%x")}'

        return title

    @property
    def body_text(self) -> str | None:
        '''The task body that typically contains information about the task'''
        if self.body:
            return self.body['content']
        return None

    @property
    def completed_date(self) -> datetime | None:
        '''The date and time in the specified time zone that the task was finished'''
        if self.completedDateTime:
            return datetime.fromisoformat(self.completedDateTime['dateTime']).astimezone(ZoneInfo(get_zoneinfo_name_by_windows_zone(self.completedDateTime['timeZone'])))
        return None

    @property
    def created_date(self) -> datetime | None:
        '''The date and time when the task was created. It is in UTC'''
        if self.createdDateTime:
            return datetime.fromisoformat(self.createdDateTime).astimezone(timezone.utc)
        return None

    @property
    def due_date(self) -> datetime | None:
        '''The date and time in the specified time zone that the task is to be finished'''
        if self.dueDateTime:
            return datetime.fromisoformat(self.dueDateTime['dateTime']).astimezone(ZoneInfo(get_zoneinfo_name_by_windows_zone(self.dueDateTime['timeZone'])))
        return None

    @property
    def last_mod_date(self) -> datetime | None:
        '''The date and time when the task was last modified. It is in UTC'''
        if self.lastModifiedDateTime:
            return datetime.fromisoformat(self.lastModifiedDateTime).astimezone(timezone.utc)
        return None

    @property
    def reminder_date(self) -> datetime | None:
        '''The date and time in the specified time zone for a reminder alert of the task to occur'''
        if self.reminderDateTime:
            return datetime.fromisoformat(self.reminderDateTime['dateTime']).astimezone(ZoneInfo(get_zoneinfo_name_by_windows_zone(self.reminderDateTime['timeZone'])))
        return None

    @property
    def start_date(self) -> datetime | None:
        '''The date and time in the specified time zone at which the task is scheduled to start'''
        if self.startDateTime:
            return datetime.fromisoformat(self.startDateTime['dateTime']).astimezone(ZoneInfo(get_zoneinfo_name_by_windows_zone(self.startDateTime['timeZone'])))
        return None

    @property
    def task_status(self) -> TaskStatus:
        '''Indicates the state or progress of the task'''
        return TaskStatus(self.status)


class ToDoConnection:
    '''**To-Do connection** is your entry point to the To-Do API

    Args:
        client_id: API client ID
        client_secret: API client secret
        token: Token obtained by method `get_token`
    '''
    _redirect: str = 'https://localhost/login/authorized'
    _scope: str = 'openid Tasks.ReadWrite offline_access'
    _authority: str = 'https://login.microsoftonline.com/common'
    _authorize_endpoint: str = '/oauth2/v2.0/authorize'
    _token_endpoint: str = '/oauth2/v2.0/token'
    _base_api_url: str = 'https://graph.microsoft.com/v1.0/me/todo/'

    def __init__(self, client_id: str, client_secret: str, token: Token) -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.token: Token = token

    @staticmethod
    def get_auth_url(client_id: str) -> Any:
        '''Get the authorization_url

        Args:
            client_id: API client ID

        Returns:
            Authorization URL to show to the user
        '''
        oa_sess = OAuth2Session(client_id, scope=ToDoConnection._scope, redirect_uri=ToDoConnection._redirect)

        authorize_url = f'{ToDoConnection._authority}{ToDoConnection._authorize_endpoint}'
        authorization_url, _ = oa_sess.authorization_url(authorize_url)

        return authorization_url

    @staticmethod
    def get_token(client_id: str, client_secret: str, redirect_resp: str) -> Any:
        '''Fetch the access token'''
        oa_sess = OAuth2Session(client_id, scope=ToDoConnection._scope, redirect_uri=ToDoConnection._redirect)
        token_url = f'{ToDoConnection._authority}{ToDoConnection._token_endpoint}'
        return oa_sess.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_resp)

    def _refresh_token(self) -> None:
        now = time.time()
        expire_time = self.token['expires_at'] - 300
        if now >= expire_time:
            token_url = f'{ToDoConnection._authority}{ToDoConnection._token_endpoint}'
            oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope,
                                    token=self.token, redirect_uri=ToDoConnection._redirect)
            new_token = oa_sess.refresh_token(token_url, client_id=self.client_id, client_secret=self.client_secret)
            self.token = new_token

    def get_lists(self, limit: int | None = 99) -> list[TaskList]:
        '''Get a list of the task lists

        Args:
            limit: The limit size of the response

        Returns:
            A list of the task lists

        Raises:
            PymstodoError: An error occurred accessing the API
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists?$top={limit}')
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())['value']
        return [TaskList(**list_data) for list_data in contents]

    def create_list(self, name: str) -> TaskList:
        '''Create a new task list

        Args:
            name: Title of the new task list

        Returns:
            A created task list

        Raises:
            PymstodoError: An error occurred accessing the API
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.post(f'{ToDoConnection._base_api_url}lists', json={'displayName': name})
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def get_list(self, list_id: str) -> TaskList:
        '''Read the properties of a task list

        Args:
            list_id: Unique identifier for the task list

        Returns:
            A task list object

        Raises:
            PymstodoError: An error occurred accessing the API
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists/{list_id}')
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def update_list(self, list_id: str, **list_data: str | bool) -> TaskList:
        '''Update the properties of a task list

        Args:
            list_id: Unique identifier for the task list
            list_data: Task properties from `TaskList` object

        Returns:
            An updated task list.

        Raises:
            PymstodoError: An error occurred accessing the API'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.patch(f'{ToDoConnection._base_api_url}lists/{list_id}', json=list_data)
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())

        return TaskList(**contents)

    def delete_list(self, list_id: str) -> bool:
        '''Delete a task list

        Args:
            list_id: Unique identifier for the task list

        Returns:
            `True` if success

        Raises:
            PymstodoError: An error occurred accessing the API'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.delete(f'{ToDoConnection._base_api_url}lists/{list_id}')
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        return True

    def get_tasks(self, list_id: str, limit: int | None = 1000, status: TaskStatusFilter | None = TaskStatusFilter.NOT_COMPLETED) -> list[Task]:
        '''Get tasks by a specified task list

        Args:
            list_id: Unique identifier for the task list
            limit: The limit size of the response
            status: The state or progress of the task

        Returns:
            Tasks of a specified task list

        Raises:
            PymstodoError: An error occurred accessing the API
        '''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        filters = {
            TaskStatusFilter.COMPLETED: "filter=status eq 'completed'",
            TaskStatusFilter.NOT_COMPLETED: "filter=status ne 'completed'",
            TaskStatusFilter.ALL: None
        }
        eff_limit = limit or 1000
        params = (
            filters.get(status or TaskStatusFilter.NOT_COMPLETED, filters[TaskStatusFilter.NOT_COMPLETED]),
            f'top={eff_limit}'
        )
        params_str = '&$'.join(filter(None, params))
        url = f'{ToDoConnection._base_api_url}lists/{list_id}/tasks?${params_str}'
        contents: list[dict[str, Any]] = []
        while (len(contents) < eff_limit or eff_limit <= 0) and url:
            resp = oa_sess.get(url)
            if not resp.ok:
                raise PymstodoError(resp.status_code, resp.reason)
            resp_content = json.loads(resp.content.decode())
            url = resp_content.get('@odata.nextLink')
            contents.extend(resp_content['value'])
        if limit:
            contents = contents[:limit]
        return [Task(**task_data) for task_data in contents]

    def create_task(self, title: str, list_id: str, due_date: datetime | None = None, body_text: str | None = None) -> Task:
        '''Create a new task in a specified task list

        Args:
            title: A brief description of the task
            list_id: Unique identifier for the task list
            due_date: The date and time that the task is to be finished
            body_text: Information about the task

        Returns:
            A created task

        Raises:
            PymstodoError: An error occurred accessing the API'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        task_data: dict[str, Any] = {'title': title}
        if due_date:
            task_data['dueDateTime'] = {'dateTime': due_date.strftime('%Y-%m-%dT%H:%M:%S.0000000'), 'timeZone': 'UTC'}
        if body_text:
            task_data['body'] = {'content': body_text, 'contentType': 'text'}
        resp = oa_sess.post(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks', json=task_data)
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def get_task(self, task_id: str, list_id: str) -> Task:
        '''Read the properties of a task

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list

        Returns:
            A task object

        Raises:
            PymstodoError: An error occurred accessing the API'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.get(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}')
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def update_task(self, task_id: str, list_id: str, **task_data: str | int | bool) -> Task:
        '''Update the properties of a task

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list
            task_data: Task properties from `Task` object

        Returns:
            An updated task

        Raises:
            PymstodoError: An error occurred accessing the API'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.patch(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}', json=task_data)
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        contents = json.loads(resp.content.decode())

        return Task(**contents)

    def delete_task(self, task_id: str, list_id: str) -> bool:
        '''Delete a task

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list

        Returns:
            `True` if success

        Raises:
            PymstodoError: An error occurred accessing the API'''
        self._refresh_token()
        oa_sess = OAuth2Session(self.client_id, scope=ToDoConnection._scope, token=self.token)
        resp = oa_sess.delete(f'{ToDoConnection._base_api_url}lists/{list_id}/tasks/{task_id}')
        if not resp.ok:
            raise PymstodoError(resp.status_code, resp.reason)

        return True

    def complete_task(self, task_id: str, list_id: str) -> Task:
        '''Complete a task

        Args:
            task_id: Unique identifier for the task
            list_id: Unique identifier for the task list

        Returns:
            A completed task

        Raises:
            PymstodoError: An error occurred accessing the API'''
        return self.update_task(task_id, list_id, status='completed')
