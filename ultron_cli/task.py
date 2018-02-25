import os
import json
import logging
import requests
from attrdict import AttrDict
from cliff.command import Command
# from prompt_toolkit import prompt

sessionfile = os.path.expanduser('~/.ultron_session.json')
with open(sessionfile) as f: session = AttrDict(json.load(f))

class Submit(Command):
    "Submit a task for all/selected clients/groups in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Submit, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-G', '--groups', nargs='*', default=[])
        parser.add_argument('-C', '--clients', nargs='*', default=[])
        parser.add_argument('-S', '--synchronous', action='store_true')
        parser.add_argument('-K', '--kwargs', type=json.loads, help='BSON encoded key-value pairs', default={})
        return parser

    def take_action(self, p):
        data = {'async': int(not p.synchronous), 'task': p.task}
        params = {'fields': 'name'}
        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)
        if len(p.clients) > 0:
            data['clientnames'] = ','.join(p.clients)
            params['clientnames'] = ','.join(p.clients)
        elif len(p.groups) > 0:
            url = '{}/groups/{}/{}'.format(session.endpoint, p.admin, p.inventory)
            data['groupnames'] = ','.join(p.groups)
            params['groupnames'] = ','.join(p.groups)
        if len(p.kwargs) > 0:
            if not isinstance(p.kwargs, dict):
                raise RuntimeError('kwargs: Must be BSON encoded key-value pairs')
            data['kwargs'] = json.dumps(p.kwargs)

        result = requests.get(url, params=params, verify=session.certfile)

        if result.status_code != requests.codes.ok:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

        targets = result.json().get('result', {})
        if len(targets) == 0:
            raise RuntimeError('ERROR: targets not found')

        result = requests.post(url, data=data, verify=session.certfile, auth=(session.username, session.password))
        if result.status_code != requests.codes.ok:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

        print('SUCCESS: Submitted task')
