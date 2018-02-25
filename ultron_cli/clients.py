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
        result = requests.get(url, params={'fields': 'name', 'dynfields': 'groups'},
                verify=session.certfile, auth=(session.username, session.password))

        if result.status_code == requests.codes.ok:
            clients = result.json().get('result', {})
            if len(clients) == 0:
                raise RuntimeError('ERROR: Clients not found')
            cols = ['name', 'groups']
            rows = [[x['name'], ', '.join(x['groups'])] for x in clients.values()]
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


class StatTasks(ShowOne):
    "Show statistics of a performed tasks"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(StatTasks, self).get_parser(prog_name)
        parser.add_argument('tasks', nargs='*', default=[])
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

        tasks = {}
        for client in clients.values():
            if not client['tasks']: continue
            for k, v in client['tasks'].items():
                if len(p.tasks) > 0 and k not in p.tasks: continue
                if k not in tasks:
                    tasks[k] = {
                        'performed on': 0, 'success': 0,
                        'failed': 0, 'pending': 0
                    }
                tasks[k]['performed on'] += 1
                tasks[k][v['status'].lower()] += 1

        return [tasks.keys(), tasks.values()]


class StatStates(ShowOne):
    "Show statistics of a client states"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(StatStates, self).get_parser(prog_name)
        parser.add_argument('states', nargs='*', default=[])
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

        states = {}
        for client in clients.values():
            for k, v in client['state'].items():
                if len(p.states) > 0 and k not in p.states: continue
                if k not in states: states[k] = {}
                if v not in states[k]: states[k][v] = 0
                states[k][v] += 1

        for k,v in states.items():
            if len(v) > 15:
                del states[k]
        return [states.keys(), states.values()]


class StatProps(ShowOne):
    "Show statistics of a client props"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(StatProps, self).get_parser(prog_name)
        parser.add_argument('props', nargs='*', default=[])
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

        props = {}
        for client in clients.values():
            for k, v in client['props'].items():
                if len(p.props) > 0 and k not in p.props: continue
                if k not in props: props[k] = {}
                if v not in props[k]: props[k][v] = 0
                props[k][v] += 1

        for k,v in props.items():
            if len(v) > 15:
                del props[k]
        return [props.keys(), props.values()]


class FilterTask(Lister):
    "List clients filtered by task status"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(FilterTask, self).get_parser(prog_name)
        parser.add_argument('task')
        parser.add_argument('value')
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

        found = set()
        for client in clients.values():
            if not client['tasks']: continue
            if client['tasks'][p.task]['status'] != p.value.upper():
                if p.value == 'performed on':
                    found.add(client['name'])
                    continue
                continue
            found.add(client['name'])

        return [['name'], [[x] for x in found]]


class FilterState(Lister):
    "List clients filtered by state"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(FilterState, self).get_parser(prog_name)
        parser.add_argument('state')
        parser.add_argument('value')
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

        found = set()
        for client in clients.values():
            if p.state not in client['state']: continue
            if str(client['state'][p.state]) != p.value:
                    continue
            found.add(client['name'])

        return [['name'], [[x] for x in found]]


class FilterProp(Lister):
    "List clients filtered by prop"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        with open(sessionfile) as f: session = AttrDict(json.load(f))
        parser = super(FilterProp, self).get_parser(prog_name)
        parser.add_argument('prop')
        parser.add_argument('value')
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

        found = set()
        for client in clients.values():
            if p.prop not in client['props']: continue
            if str(client['props'][p.prop]) != p.value:
                    continue
            found.add(client['name'])

        return [['name'], [[x] for x in found]]
