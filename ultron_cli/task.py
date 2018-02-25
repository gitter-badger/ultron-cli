import os
import json
import logging
import requests
from attrdict import AttrDict
from cliff.command import Command
from cliff.show import ShowOne


sessionfile = os.path.expanduser('~/.ultron_session.json')


class Submit(Command):
    "Submit a task for all clients in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Submit, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-S', '--synchronous', action='store_true')
        parser.add_argument('-K', '--kwargs', type=json.loads, help='BSON encoded key-value pairs', default={})
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {'async': int(not p.synchronous), 'task': p.task}
        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)
        if len(p.kwargs) > 0:
            if not isinstance(p.kwargs, dict):
                raise RuntimeError('kwargs: Must BSON encoded key-value pairs')
            data['kwargs'] = json.dumps(p.kwargs)

        result = requests.post(url, data=data, verify=session.certfile, auth=(session.username, session.password))
        if result.status_code != requests.codes.ok:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

        print('SUCCESS: Submitted task')


class Stat(ShowOne):
    "Show statistics of a performed task in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Stat, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        result = requests.get(url, verify=session.certfile)
        if result.status_code != requests.codes.ok:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

        clients = result.json().get('result', {})

        if len(clients) == 0:
            raise RuntimeError('ERROR: Clients not found')

        status = []
        for client in clients.values():
            if p.task not in client.get('tasks', {}): continue
            status.append(client['tasks'][p.task]['status'])

        return [
            ['total', 'performed on', 'success', 'failed', 'pending'],
            [len(clients), len(status), status.count('SUCCESS'), status.count('FAILED'), status.count('PENDING')]
        ]

