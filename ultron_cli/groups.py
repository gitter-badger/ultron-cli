import os
import json
import logging
import requests
from attrdict import AttrDict
from cliff.lister import Lister
from cliff.command import Command
from prompt_toolkit import prompt

sessionfile = os.path.expanduser('~/.ultron_session.json')
with open(sessionfile) as f: session = AttrDict(json.load(f))

class Get(Lister):
    "Get groups"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-F', '--fields', nargs='*', default=[])
        return parser

    def take_action(self, p):
        params = {}
        if len(p.groups) > 0:
            params['groupnames'] = ','.join(p.groups)
        if len(p.fields) > 0:
            params['fields'] = ','.join(p.fields)

        url = '{}/groups/{}/{}'.format(session.endpoint, p.admin, p.inventory)
        result = requests.get(url, params=params, verify=session.certfile)

        if result.status_code == requests.codes.ok:
            groups = result.json().get('result', {})
            if len(groups) == 0:
                raise RuntimeError('ERROR: groups not found')
            cols = list(groups.values())[0].keys()
            rows = [[x[c] for c in cols] for x in groups.values()]
            return [cols, rows]
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class New(Command):
    "New groups"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-c', '--clients', nargs='*')
        parser.add_argument('-d', '--description', default='')
        parser.add_argument('-p', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        if len(p.groups) == 0:
            groupnames = prompt('Enter hostnames and press ESC+ENTER\n> ', multiline=True).split()
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
    "Update groups"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-c', '--clients', nargs='*', default=[])
        parser.add_argument('-r', '--remove', action='store_true', default=False)
        parser.add_argument('-d', '--description', default=None)
        parser.add_argument('-p', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
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
    "Delete groups"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('groups', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
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


