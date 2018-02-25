import os
import json
import logging
import requests
from attrdict import AttrDict
from cliff.command import Command
from prompt_toolkit import prompt


sessionfile = os.path.expanduser('~/.ultron_session.json')
with open(sessionfile) as f: session = AttrDict(json.load(f))


class Connect(Command):
    "Connect with Ultron API"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Connect, self).get_parser(prog_name)
        parser.add_argument('endpoint', default=None)
        parser.add_argument('-u', '--username', default=None)
        parser.add_argument('-p', '--password', default=None)
        parser.add_argument('-i', '--inventory', default=None)
        parser.add_argument('-c', '--certfile', default=False)
        return parser

    def take_action(self, parsed):

        if not parsed.endpoint:
            endpoint = prompt('API endpoint: ', default=session.endpoint)
        else:
            endpoint = parsed.endpoint

        if not parsed.username:
            username = prompt('Username: ', default=session.username)
        else:
            username = parsed.username

        if not parsed.password:
            password = prompt('Password: ', is_password=True, default=session.password)
        else:
            password = parsed.password

        if parsed.inventory is None:
            inventory = prompt('Enter default inventory: ', default=session.inventory)
        else:
            inventory = parsed.inventory

        self.log.info('Connecting to {} as {}...'.format(endpoint, username))

        result = requests.get('{}/admins/{}'.format(endpoint, username),
                              auth=(username, password), verify=parsed.certfile)
        if result.status_code == requests.codes.ok:
            with open(sessionfile, 'w') as f:
                json.dump({
                    'endpoint': endpoint,
                    'username': username,
                    'password': password,
                    'certfile': parsed.certfile,
                    'inventory': inventory
                }, f, indent=4)
            os.chmod(sessionfile, 0o600)
            self.log.info('Connected to Ultron API')
        else:
            raise RuntimeError('ERROR: {}: {}'.format(result.status_code, result.json().get('message')))


class Disconnect(Command):
    "Disconnect and destroy session"

    log = logging.getLogger(__name__)

    def take_action(self, parsed):
        os.remove(sessionfile)
        self.log.info('Disconnected from Ultron API')

class DefaultInventory(Command):
    "Sel default inventory"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DefaultInventory, self).get_parser(prog_name)
        parser.add_argument('inventory')
        return parser

    def take_action(self, parsed):
        session['inventory'] = parsed.inventory
        with open(sessionfile, 'w') as f:
            json.dump(session, f, indent=4)
        self.log.info('Default inventory is set as: '+session['inventory'])
