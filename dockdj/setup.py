import os
from dockdj.du_settings import CONFIG_FILE
from fabric import Connection
import yaml
from invoke import exceptions


def setup(verbose=False):
    hide = not verbose
    if not os.path.isfile(CONFIG_FILE):
        print("Please run django_up init to create config file")
        return

    with open(CONFIG_FILE, 'r') as the_file:
        config_yaml = yaml.load(the_file)

    server = config_yaml['server']
    with Connection(
            host=server['host'],
            user=server['username'],
            connect_kwargs={'key_filename': server['pem']}) as cnx:
        try:
            cnx.run('docker -v', hide=hide)
            cnx.run('docker-compose --version', hide=hide)
            print('Docker & Docker compose already present')
        except exceptions.UnexpectedExit:
            print('Docker or docker compose not present')
            install_docker(cnx, hide=hide)


def install_docker(cnx, hide=True):
    try:
        cnx.run('docker -v', hide=hide)
    except exceptions.UnexpectedExit:
        print('Installing docker')
        cnx.run('sudo apt-get update', hide=hide)
        cnx.run('sudo apt-get install unzip apt-transport-https ca-certificates curl software-properties-common -y',
                hide=hide)
        cnx.run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -', hide=hide)
        cnx.run('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
                hide=hide)
        cnx.run('sudo apt-get update', hide=hide)
        cnx.run('sudo apt-get install docker-ce -y', hide=hide)
        print('Docker installed')

    try:
        cnx.run('docker-compose --version', hide=hide)
    except exceptions.UnexpectedExit:
        print('Installing docker compose')
        cnx.run('sudo curl -L https://github.com/docker/compose/releases/download/1.23.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose', hide=hide)
        cnx.run('sudo chmod +x /usr/local/bin/docker-compose',
                hide=hide)
        print('Docker compose installed')
