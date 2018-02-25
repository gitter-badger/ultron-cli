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
    "List all admins"

    log = logging.getLogger(__name__)

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

        url = '{}/admins'.format(session.endpoint)
        result = requests.get(url, params={'fields': 'name'}, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admins = result.json().get('result', {})
            if len(admins) == 0:
                raise RuntimeError('ERROR: Admins not found')
            cols = ['name']
            rows = [[x] for x in admins.keys()]
            return [cols, rows]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Show(ShowOne):
    "Show details of an admin"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('admin')
        parser.add_argument('-F', '--fields', nargs='*', default=[])
        parser.add_argument('-D', '--dynfields', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

        params = {}
        if len(p.fields) > 0:
            params['fields'] = ','.join(p.fields)
        if len(p.dynfields) > 0:
            params['dynfields'] = ','.join(p.dynfields)

        url = '{}/admins/{}'.format(session.endpoint, p.admin)
        result = requests.get(url, params=params, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admin = result.json().get('result',{}).get(p.admin)
            if not admin:
                raise RuntimeError('ERROR: Admin not found')
            return [admin.keys(), admin.values()]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class New(Command):
    "Add new admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*')
        parser.add_argument('-p', '--password', default=None)
        parser.add_argument('-P', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

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
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Update(Command):
    "Update details of existing admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        parser.add_argument('-p', '--password', default=None)
        parser.add_argument('-P', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

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
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Delete(Command):
    "Delete admins"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('admins', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

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
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class ListTasks(Lister):
    "List allowed tasks of an admin"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

        parser = super(ListTasks, self).get_parser(prog_name)
        parser.add_argument('-A', '--admin', default=session.username)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

        params = {'dynfields': 'allowed_tasks', 'fields': 'name'}

        url = '{}/admins/{}'.format(session.endpoint, p.admin)
        result = requests.get(url, params=params, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admin = result.json().get('result',{}).get(p.admin)
            if not admin:
                raise RuntimeError('ERROR: Admin not found')
            cols = ['allowed_tasks']
            rows = [[x] for x in admin['allowed_tasks']]
            return [cols, rows]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class ListInventories(Lister):
    "List created inventories by an admin"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

        parser = super(ListInventories, self).get_parser(prog_name)
        parser.add_argument('-A', '--admin', default=session.username)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))

        params = {'dynfields': 'inventories', 'fields': 'name'}

        url = '{}/admins/{}'.format(session.endpoint, p.admin)
        result = requests.get(url, params=params, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            admin = result.json().get('result',{}).get(p.admin)
            if not admin:
                raise RuntimeError('ERROR: Admin not found')
            cols = ['inventories']
            rows = [[x] for x in admin['inventories']]
            return [cols, rows]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))
