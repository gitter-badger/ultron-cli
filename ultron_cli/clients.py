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
    "Get clients"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-F', '--fields', nargs='*', default=[])
        parser.add_argument('-D', '--dynfields', nargs='*', default=[])
        return parser

    def take_action(self, p):
        params = {}
        if len(p.clients) > 0:
            params['clientnames'] = ','.join(p.clients)
        if len(p.fields) > 0:
            params['fields'] = ','.join(p.fields)
        if len(p.dynfields) > 0:
            params['dynfields'] = ','.join(p.dynfields)

        url = '{}/clients/{}/{}'.format(session.endpoint, p.admin, p.inventory)
        result = requests.get(url, params=params, verify=session.certfile)

        if result.status_code == requests.codes.ok:
            clients = result.json().get('result', {})
            if len(clients) == 0:
                raise RuntimeError('ERROR: Clients not found')
            cols = list(clients.values())[0].keys()
            rows = [[x[c] for c in cols] for x in clients.values()]
            return [cols, rows]
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class New(Command):
    "New clients"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-p', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
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
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Update(Command):
    "Update clients"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        parser.add_argument('-p', '--props', nargs='*', default=[])
        return parser

    def take_action(self, p):
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
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Delete(Command):
    "Delete clients"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('clients', nargs='*', default=[])
        parser.add_argument('-a', '--admin', default=session.username)
        parser.add_argument('-i', '--inventory', default=session.inventory)
        return parser

    def take_action(self, p):
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
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


