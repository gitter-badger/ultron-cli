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
    "List all clients in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)
        result = requests.get(url, params={'fields': 'name'}, verify=session.certfile,
                              auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            clients = result.json().get('result', {})
            if len(clients) == 0:
                raise RuntimeError('ERROR: Clients not found')
            cols = ['name']
            rows = [[x] for x in clients.keys()]
            return [cols, rows]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Show(ShowOne):
    "Show details of a client"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('client')
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
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

        url = '{}/clients/{}/{}/{}'.format(session.endpoint, p.admin, p.inventory, p.client)
        result = requests.get(url, params=params, verify=session.certfile)

        if result.status_code == requests.codes.ok:
            client = result.json().get('result',{}).get(p.client)
            if not client:
                raise RuntimeError('ERROR: Client not found')
            return [client.keys(), client.values()]
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class New(Command):
    "Add new clients to inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-P', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        if len(p.clients) == 0:
            clientnames = prompt('Enter hostnames and press ESC+ENTER\n> ', multiline=True).split()
        else:
            clientnames = p.clients

        data = {'clientnames': ','.join(set(clientnames))}
        if len(p.props) > 0:
            try:
                data['props'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.props
                })
            except:
                raise RuntimeError('ERROR: Invalid props format. Example format: a=123 b=abc c=xyz')

        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate if already exists
        result = requests.get(url, params={'clientnames': data['clientnames'], 'fields': 'name'},
                              verify=session.certfile)
        clients = result.json().get('result')
        if len(clients) > 0:
            raise RuntimeError('ERROR: Duplicate clients: {}'.format(', '.join(clients.keys())))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Created new clients')
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Update(Command):
    "Update details of existing clients"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-P', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {}
        if len(p.clients) > 0:
            data = {'clientnames': ','.join(set(p.clients))}
        if len(p.props) > 0:
            try:
                data['props'] = json.dumps({
                    x.split('=')[0]: '='.join(x.split('=')[1:]) for x in p.props
                })
            except:
                raise RuntimeError('ERROR: Invalid props format. Example format: a=123 b=abc c=xyz')

        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate no extra clients
        if len(p.clients) > 0:
            result = requests.get(url, params={'clientnames': data['clientnames'], 'fields': 'name'},
                                  verify=session.certfile)
            clients = result.json().get('result')
            if len(clients) != len(p.clients):
                raise RuntimeError('ERROR: Clients not found: {}'.format(', '.join(set(set(p.clients)-clients.keys()))))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Updated clients')
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Delete(Command):
    "Delete clients from inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {}
        if len(p.clients) > 0:
            data = {'clientnames': ','.join(set(p.clients))}

        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate no extra clients
        if len(p.clients) > 0:
            result = requests.get(url, params={'clientnames': data['clientnames'], 'fields': 'name'},
                                  verify=session.certfile)
            clients = result.json().get('result')
            if len(clients) != len(p.clients):
                raise RuntimeError('ERROR: Clients not found: {}'.format(', '.join(set(set(p.clients)-clients.keys()))))

        result = requests.delete(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Deleted clients')
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

class Perform(Command):
    "Perform a task on all/selected clients in inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(Perform, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('clients',  nargs='*', default=[])
        parser.add_argument('-A', '--admin', default=session.username)
        parser.add_argument('-I', '--inventory', default=session.inventory)
        parser.add_argument('-S', '--synchronous', action='store_true')
        parser.add_argument('-K', '--kwargs', type=json.loads, help='BSON encoded key-value pairs', default={})
        return parser

    def take_action(self, p):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        data = {'async': int(not p.synchronous), 'task': p.task}

        if len(p.clients) > 0:
            data['clientnames'] = ','.join(set(p.clients))

        if len(p.kwargs) > 0:
            if not isinstance(p.kwargs, dict):
                raise RuntimeError('kwargs: Must be BSON encoded key-value pairs')
            data['kwargs'] = json.dumps(p.kwargs)


        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)

        # Validate no extra clients
        if len(p.clients) > 0:
            result = requests.get(url, params={'clientnames': data['clientnames'], 'fields': 'name'},
                                  verify=session.certfile)
            clients = result.json().get('result')
            if len(clients) != len(p.clients):
                raise RuntimeError('ERROR: Clients not found: {}'.format(', '.join(set(set(p.clients)-clients.keys()))))

        result = requests.post(url, data=data, verify=session.certfile,
                               auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            print('SUCCESS: Submitted task')
            return
        raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))

