from setuptools import setup, find_packages
from codecs import open
from os import path
from ultron_cli.config import VERSION

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Requirements for installation
with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()

setup(
    name='ultron-cli',
    version=VERSION,

    description='Command-line interface to interact with Ultron API',
    long_description=long_description,

    author='Arijit Basu',
    author_email='sayanarijit@gmail.com',

    url='https://github.com/rapidstack/ultron-cli',
    # download_url='https://github.com/rapidstack/ultron-cli/archive/{}.tar.gz'.format(VERSION),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.2',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'Operating System :: POSIX'
    ],

    scripts=[],

    provides=[],
    install_requires=install_requirements,

    namespace_packages=[],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'ultron = ultron_cli.main:main'
        ],
        'ultron.cli': [
            'connect = ultron_cli.session:Connect',
            'disconnect = ultron_cli.session:Disconnect',
            'inventory = ultron_cli.session:DefaultInventory',

            'new admins = ultron_cli.admins:New',
            'list admins = ultron_cli.admins:List',
            'update admins = ultron_cli.admins:Update',
            'delete admins = ultron_cli.admins:Delete',
            'show admin = ultron_cli.admins:Show',

            'list tasks = ultron_cli.admins:ListTasks',
            'list inventories = ultron_cli.admins:ListInventories',

            'new groups = ultron_cli.groups:New',
            'list groups = ultron_cli.groups:List',
            'update groups = ultron_cli.groups:Update',
            'delete groups = ultron_cli.groups:Delete',
            'show group = ultron_cli.groups:Show',
            'perform on group = ultron_cli.groups:Perform',
            'append clients to group = ultron_cli.groups:AppendClients',
            'remove clients from group = ultron_cli.groups:RemoveClients',

            'new clients = ultron_cli.clients:New',
            'list clients = ultron_cli.clients:List',
            'update clients = ultron_cli.clients:Update',
            'delete clients = ultron_cli.clients:Delete',
            'perform on clients = ultron_cli.clients:Perform',
            'show client = ultron_cli.clients:Show'
        ]
    },

    zip_safe=False,
)
