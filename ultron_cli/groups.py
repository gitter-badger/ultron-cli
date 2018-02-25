import os
import json
import logging
import requests
from attrdict import AttrDict
from cliff.lister import Lister
from cliff.command import Command
from cliff.show import ShowOne
from prompt_toolkit import prompt


sessionfile = os.path.expanduser('~/.ultron_session.json')


class List(Lister):
    "List all groups in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        url = '{}/groups/{}/{}'.format(session.endpoint, p.admin, p.inventory)
        result = requests.get(url, params={'fields': 'name'}, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            groups = result.json().get('result', {})
            if len(groups) == 0:
                raise RuntimeError('ERROR: Groups not found')
            cols = ['name']
            rows = [[x] for x in groups.keys()]
            return [cols, rows]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

class Show(ShowOne):
    "Show details of a group"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('group')
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-F', '--fields', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        params = {}
        if len(p.fields) > 0:
            params['fields'] = ','.join(p.fields)

        url = '{}/groups/{}/{}/{}'.format(session.endpoint, p.admin, p.inventory, p.group)
        result = requests.get(url, params=params, verify=session.certfile)

        if result.status_code == requests.codes.ok:
            group = result.json().get('result',{}).get(p.group)
            if not group:
                raise RuntimeError('ERROR: group not found')
            return [group.keys(), group.values()]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class New(Command):
    "Create new groups in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-C', '--clients', nargs='*')
        parser.add_argument('-D', '--description', default='')
        parser.add_argument('-P', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        if len(p.groups) == 0:
            groupnames = prompt('Enter group names and press ESC+ENTER\n> ', multiline=True).splitlines()
        else:
            groupnames = p.groups

        data = {
            'groupnames': ','.join(set(groupnames)), ''
            'description': p.description,
            'clientnames': p.clients
        }
        if len(p.props) > 0:
            try:
                data['props'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.props
                })
            except:
                raise RuntimeError('ERROR: Invalid props format. Example format: a=123 b=abc c=xyz')

        url = '{}/groups/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate if already exists
        result = requests.get(url, params={'groupnames': data['groupnames'], 'fields': 'name'},
                              verify=session.certfile)
        groups = result.json().get('result')
        if len(groups) > 0:
            raise RuntimeError('ERROR: Duplicate groups: {}'.format(', '.join(groups.keys())))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Created new groups')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Update(Command):
    "Update existing groups in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-C', '--clients', nargs='*', default=[])
        parser.add_argument('-R', '--remove', action='store_true')
        parser.add_argument('-D', '--description', default=None)
        parser.add_argument('-P', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {}
        if len(p.groups) > 0:
            data['groupnames'] = ','.join(set(p.groups))
        if len(p.clients) > 0:
            data['clientnames'] = ','.join(set(p.clients))
        if p.remove:
            data['action'] = 'remove'
        if p.description is not None:
            data['description'] = p.description
        if len(p.props) > 0:
            try:
                data['props'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.props
                })
            except:
                raise RuntimeError('ERROR: Invalid props format. Example format: a=123 b=abc c=xyz')

        url = '{}/groups/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate no extra groups
        if len(p.groups) > 0:
            result = requests.get(url, params={'groupnames': data['groupnames'], 'fields': 'name'},
                                  verify=session.certfile)
            groups = result.json().get('result')
            if len(groups) != len(p.groups):
                raise RuntimeError('ERROR: groups not found: {}'.format(', '.join(set(set(p.groups)-groups.keys()))))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Updated groups')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Delete(Command):
    "Delete groups from inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {}
        if len(p.groups) > 0:
            data = {'groupnames': ','.join(set(p.groups))}

        url = '{}/groups/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate no extra groups
        if len(p.groups) > 0:
            result = requests.get(url, params={'groupnames': data['groupnames'], 'fields': 'name'},
                                  verify=session.certfile)
            groups = result.json().get('result')
            if len(groups) != len(p.groups):
                raise RuntimeError('ERROR: groups not found: {}'.format(', '.join(set(set(p.groups)-groups.keys()))))

        result = requests.delete(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Deleted groups')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

class Perform(Command):
    "Perform a task a group"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Perform, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('group')
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-S', '--synchronous', action='store_true')
        parser.add_argument('-K', '--kwargs', type=json.loads, help='BSON encoded key-value pairs', default={})
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {'async': int(not p.synchronous), 'task': p.task}

        if len(p.kwargs) > 0:
            if not isinstance(p.kwargs, dict):
                raise RuntimeError('kwargs: Must be BSON encoded key-value pairs')
            data['kwargs'] = json.dumps(p.kwargs)

        url = '{}/groups/{}/{}/{}'.format(session.endpoint, p.admin, p.inventory, p.group)

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Submitted task')
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

