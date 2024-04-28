# pymstodo ✔️
[![PyPI](https://img.shields.io/pypi/v/pymstodo.svg)](https://pypi.org/project/pymstodo/) [![Build Status](https://github.com/inbalboa/pymstodo/actions/workflows/main.yml/badge.svg)](https://github.com/inbalboa/pymstodo/actions/workflows/main.yml) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### Python wrapper to deal with [Microsoft To Do](https://to-do.live.com).

## Installation
```
pip3 install pymstodo
```

## Requirements
* python >= 3.10
* requests_oauthlib >= 1.3.0

## Usage
1. [Get an API key](https://github.com/inbalboa/pymstodo/blob/master/GET_KEY.md) before using `pymstodo`.
2. Use it to initialize client. Here is an example:
```python
from pymstodo import ToDoConnection

client_id = 'PLACE YOUR CLIENT ID'
client_secret = 'PLACE YOUR CLIENT SECRET'

auth_url = ToDoConnection.get_auth_url(client_id)
redirect_resp = input(f'Go here and authorize:\n{auth_url}\n\nPaste the full redirect URL below:\n')
token = ToDoConnection.get_token(client_id, client_secret, redirect_resp)  # you have to save it somewhere
print(token)
todo_client = ToDoConnection(client_id=client_id, client_secret=client_secret, token=token)

lists = todo_client.get_lists()
task_list = lists[0]
tasks = todo_client.get_tasks(task_list.list_id)

print(task_list)
print(*tasks, sep='\n')
```
3. Full documentation: https://inbalboa.github.io/pymstodo/

4. API description by Microsoft see at https://docs.microsoft.com/en-us/graph/api/resources/todo-overview
