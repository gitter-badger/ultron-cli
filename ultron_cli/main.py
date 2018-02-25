import sys
import os
import json
from cliff.app import App
from cliff.commandmanager import CommandManager
from ultron_cli.config import VERSION


class UltronCli(App):
    """ Cli for ultron API """
    def __init__(self):
        super(UltronCli, self).__init__(
            description='Command-line interface to interact with Ultron API',
            version=VERSION,
            command_manager=CommandManager('ultron.cli'),
            deferred_help=True,
            )

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')
        sessionfile = os.path.expanduser('~/.ultron_session.json')
        if not os.path.exists(sessionfile):
            with open(sessionfile, 'w') as f:
                json.dump({
                    'username': os.getlogin(),
                    'password': 'fakepass',
                    'endpoint': 'https://localhost:5050/api/v1.0',
                    'inventory': ''
                }, f, indent=4)
            os.chmod(sessionfile, 0o600)

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    ultron_cli = UltronCli()
    return ultron_cli.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
