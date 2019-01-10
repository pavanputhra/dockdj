import os
from dockdj.du_settings import CONFIG_FILE
from fabric import Connection
import yaml
from invoke import exceptions


def logs(verbose=False):
    if not os.path.isfile(CONFIG_FILE):
        print("Please run django_up init to create config file")
        return

    with open(CONFIG_FILE, 'r') as the_file:
        config_yaml = yaml.load(the_file)

    app_name = config_yaml['app']['name']

    for server in config_yaml['servers']:
        with Connection(
                host=server['host'],
                user=server['username'],
                connect_kwargs={'key_filename': server['pem']}) as cnx:
            try:
                cnx.run(f'docker logs {app_name}')
            except exceptions.UnexpectedExit:
                print('Some thing went wrong')
