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

    for server in config_yaml['servers']:
        with Connection(
                host=server['host'],
                user=server['username'],
                connect_kwargs={'key_filename': server['pem']}) as cnx:
            try:
                cnx.run('docker -v', hide=hide)
                print('Docker already present')
            except exceptions.UnexpectedExit:
                print('Docker not present')
                install_docker(cnx, hide=hide)


def install_docker(cnx, hide=True):
    print('Installing docker')
    cnx.run('sudo apt-get update', hide=hide)
    cnx.run('sudo apt-get install unzip apt-transport-https ca-certificates curl software-properties-common -y',
            hide=hide)
    cnx.run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -', hide=hide)
    cnx.run('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
            hide=hide)
    cnx.run('sudo apt-get update', hide=hide)
    cnx.run('sudo apt-get install docker-ce -y', hide=hide)
    print('Completed')
