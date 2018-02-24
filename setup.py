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
    download_url='https://github.com/rapidstack/ultron-cli/archive/{}.tar.gz'.format(VERSION),

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
            'get admins = ultron_cli.admins:Get',
            'update admins = ultron_cli.admins:Update',
            'delete admins = ultron_cli.admins:Delete',

            'get tasks = ultron_cli.admins:GetTasks',
            'get inventories = ultron_cli.admins:GetInventories',

            'new groups = ultron_cli.groups:New',
            'get groups = ultron_cli.groups:Get',
            'update groups = ultron_cli.groups:Update',
            'delete groups = ultron_cli.groups:Delete',

            'new clients = ultron_cli.clients:New',
            'get clients = ultron_cli.clients:Get',
            'update clients = ultron_cli.clients:Update',
            'delete clients = ultron_cli.clients:Delete',

            'submit task = ultron_cli.task:Submit'
            # 'stat task = ultron_cli.task:Stat'
        ]
    },

    zip_safe=False,
)
