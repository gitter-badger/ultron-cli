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
    "Get admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        parser.add_argument('-F', '--fields', nargs='*', default=[])
        parser.add_argument('-D', '--dynfields', nargs='*', default=[])
        return parser

    def take_action(self, p):
        params = {}
        if len(p.admins) > 0:
            params['adminnames'] = ','.join(p.admins)
        if len(p.fields) > 0:
            params['fields'] = ','.join(p.fields)
        if len(p.dynfields) > 0:
            params['dynfields'] = ','.join(p.dynfields)

        url = '{}/admins'.format(session.endpoint)
        result = requests.get(url, params=params, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admins = result.json().get('result', {})
            if len(admins) == 0:
                raise RuntimeError('ERROR: Admins not found')
            cols = list(admins.values())[0].keys()
            rows = [[x[c] for c in cols] for x in admins.values()]
            return [cols, rows]
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class New(Command):
    "New admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*')
        parser.add_argument('-P', '--password', default=None)
        parser.add_argument('-p', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        if len(p.admins) == 0:
            adminnames = prompt('Enter usernames and press ESC+ENTER\n> ', multiline=True).split()
        else:
            adminnames = p.admins

        data = {'adminnames': ','.join(set(adminnames))}

        if p.password:
            data['password'] = p.password

        if len(p.props) > 0:
            try:
                data['props'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.props
                })
            except:
                raise RuntimeError('ERROR: Invalid props format. Example format: a=123 b=abc c=xyz')

        url = '{}/admins'.format(session.endpoint)

        # Validate if already exists
        result = requests.get(url, params={'adminnames': data['adminnames'], 'fields': 'name'},
                              verify=session.certfile, auth=(session.username, session.password))
        admins = result.json().get('result')
        if len(admins) > 0:
            raise RuntimeError('ERROR: Duplicate admins: {}'.format(', '.join(admins.keys())))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Created new admins')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Update(Command):
    "Update admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        parser.add_argument('-P', '--password', default=None)
        parser.add_argument('-p', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        data = {}
        if len(p.admins) > 0:
            data['adminnames'] = ','.join(p.admins)
        if p.password:
            data['password'] = p.password
        if len(p.props) > 0:
            try:
                data['props'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.props
                })
            except:
                raise RuntimeError('ERROR: Invalid props format. Example format: a=123 b=abc c=xyz')

        url = '{}/admins'.format(session.endpoint)

        # Validate no extra admins
        if len(p.admins) > 0:
            result = requests.get(url, params={'adminnames': data['adminnames'], 'fields': 'name'},
                                  verify=session.certfile, auth=(session.username, session.password))
            admins = result.json().get('result')
            if len(admins) != len(p.admins):
                raise RuntimeError('ERROR: admins not found: {}'.format(', '.join(set(set(p.admins)-admins.keys()))))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Updated admins')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Delete(Command):
    "Delete admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        return parser

    def take_action(self, p):
        data = {}
        if len(p.admins) > 0:
            data['adminnames'] = ','.join(p.admins)

        url = '{}/admins'.format(session.endpoint)

        # Validate no extra admins
        if len(p.admins) > 0:
            result = requests.get(url, params={'adminnames': data['adminnames'], 'fields': 'name'},
                                  verify=session.certfile, auth=(session.username, session.password))
            admins = result.json().get('result')
            if len(admins) != len(p.admins):
                raise RuntimeError('ERROR: admins not found: {}'.format(', '.join(set(set(p.admins)-admins.keys()))))

        result = requests.delete(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Deleted admins')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class GetTasks(Lister):
    "Get allowed tasks"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GetTasks, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        return parser

    def take_action(self, p):
        params = {'dynfields': 'allowed_tasks', 'fields': 'name'}
        if len(p.admins) > 0:
            params['admins'] = ','.join(p.admins)

        url = '{}/admins'.format(session.endpoint)
        result = requests.get(url, params=params, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admins = result.json().get('result', {})
            if len(admins) == 0:
                raise RuntimeError('ERROR: Admins not found')
            cols = list(admins.values())[0].keys()
            rows = [[x[c] for c in cols] for x in admins.values()]
            return [cols, rows]
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class GetInventories(Lister):
    "Get created inventories"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GetInventories, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        return parser

    def take_action(self, p):
        params = {'dynfields': 'inventories', 'fields': 'name'}
        if len(p.admins) > 0:
            params['admins'] = ','.join(p.admins)

        url = '{}/admins'.format(session.endpoint)
        result = requests.get(url, params=params, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admins = result.json().get('result', {})
            if len(admins) == 0:
                raise RuntimeError('ERROR: Admins not found')
            cols = list(admins.values())[0].keys()
            rows = [[x[c] for c in cols] for x in admins.values()]
            return [cols, rows]
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))
