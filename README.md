# ultron-cli
Command-line interface to interact with Ultron API

```bash
~ ultron --help

usage: ultron [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

Command-line interface to interact with Ultron API

optional arguments:
  --version            show program's version number and exit
  -v, --verbose        Increase verbosity of output. Can be repeated.
  -q, --quiet          Suppress output except warnings and errors.
  --log-file LOG_FILE  Specify a file to log output. Disabled by default.
  -h, --help           Show help message and exit.
  --debug              Show tracebacks on errors.

Commands:
  complete       print bash completion command (cliff)
  connect        Connect with Ultron API
  delete admins  Delete admins
  delete clients  Delete clients
  delete groups  Delete groups
  disconnect     Destroy session
  get admins     Get admins
  get clients    Get clients
  get groups     Get groups
  get inventories  Get created inventories
  get tasks      Get allowed tasks
  help           print detailed help for another command (cliff)
  inventory      Sel default inventory
  new admins     New admins
  new clients    New clients
  new groups     New groups
  submit task    Submit task
  update admins  Update admins
  update clients  Update clients
  update groups  Update groups
```
