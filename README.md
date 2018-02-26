# ultron-cli

[![Join the chat at https://gitter.im/rapidstack/ultron-cli](https://badges.gitter.im/rapidstack/ultron-cli.svg)](https://gitter.im/rapidstack/ultron-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
Command-line interface to interact with Ultron API

```
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
  append clients to group  Append clients to a group
  complete       print bash completion command (cliff)
  connect        Connect with Ultron API
  delete admins  Delete admins
  delete clients  Delete clients from inventory
  delete groups  Delete groups from inventory
  disconnect     Disconnect and destroy session
  filter client prop  List clients filtered by prop
  filter client state  List clients filtered by state
  filter client task  List clients filtered by task status
  help           print detailed help for another command (cliff)
  inventory      Get or set default inventory
  list admins    List all admins
  list clients   List all clients in inventory
  list groups    List all groups in inventory
  list inventories  List created inventories by an admin
  list tasks     List allowed tasks of an admin
  new admins     Add new admins
  new clients    Add new clients to inventory
  new groups     Create new groups in inventory
  perform on clients  Perform a task on all/selected clients in inventory
  perform on group  Perform a task a group
  remove clients from group  Remove clients from a group
  show admin     Show details of an admin
  show client    Show details of a client
  show group     Show details of a group
  stat client props  Show statistics of a client props
  stat client states  Show statistics of a client states
  stat client tasks  Show statistics of a performed tasks
  update admins  Update details of existing admins
  update clients  Update details of existing clients
  update groups  Update existing groups in inventory
```
