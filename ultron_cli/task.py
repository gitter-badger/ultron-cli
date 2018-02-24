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
    "Submit task"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Submit, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-g', '--groups', nargs='*', default=[])
        parser.add_argument('-c', '--clients', nargs='*', default=[])
        parser.add_argument('-A', '--async', action='store_true', default=True)
        parser.add_argument('-k', '--kwargs', nargs='*', default=[])
        return parser

    def take_action(self, p):
        data = {'async': int(p.async), 'task': p.task}
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
            try:
                data['kwargs'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.kwargs
                })
            except:
                raise RuntimeError('ERROR: Invalid kwargs format. Example format: a=123 b=\'{"a": "A"}\' c=\'["a", 1, true]\'')

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
