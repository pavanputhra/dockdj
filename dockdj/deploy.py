import os
from dockdj.util import read_config_files
from fabric import Connection
from invoke import exceptions
import shutil

server_dir = '/var/tmp/dockdj'


def manage(args='', verbose=False):
    hide = not verbose
    config_yaml, settings_py = read_config_files()
    server = config_yaml['servers'][0]
    app_name = config_yaml["app"]["name"]
    app_dir = config_yaml['app']['path']

    print('Zipping the django project')

    shutil.make_archive(app_name, 'zip', app_dir)

    with Connection(
            host=server['host'],
            user=server['username'],
            connect_kwargs={'key_filename': server['pem']}) as cnx:
        try:
            build_docker_image(cnx, config_yaml, settings_py, hide)
            server_env_opts = prepare_server_env_cmd_args(server)
            cmd_args = ' '.join(args)
            manage_cmd = f'python manage.py {cmd_args}'
            print(manage_cmd)
            cnx.run(
                f'docker run {server_env_opts} --entrypoint "/bin/bash" {app_name} -c "{manage_cmd}"')
            cnx.run(f'rm -Rf {server_dir}', hide=hide)
        except exceptions.UnexpectedExit:
            print('Some exception')

    os.remove(f'{app_name}.zip')


def deploy(verbose=False):
    hide = not verbose

    config_yaml, settings_py = read_config_files()

    print('Zipping the django project')
    app_dir = config_yaml['app']['path']
    app_name = config_yaml["app"]["name"]

    shutil.make_archive(app_name, 'zip', app_dir)

    for server in config_yaml['servers']:
        with Connection(
                host=server['host'],
                user=server['username'],
                connect_kwargs={ 'key_filename': server['pem']}) as cnx:
            try:
                build_docker_image(cnx, config_yaml, settings_py, hide)
                run_docker_app(cnx, config_yaml, server, hide)
            except exceptions.UnexpectedExit:
                print('Some exception')

    os.remove(f'{app_name}.zip')


def run_docker_app(cnx, config_yaml, server, hide):
    app_name = config_yaml["app"]["name"]
    app_port = config_yaml['app']['port']
    server_env_opts = prepare_server_env_cmd_args(server)

    try:
        cnx.run(f'docker stop {app_name}', hide=hide)
        cnx.run(f'docker rm {app_name}', hide=hide)
    except exceptions.UnexpectedExit:
        pass
    print('Trying to run app in docker')
    cnx.run(f'docker run -d -p {app_port}:80 {server_env_opts} --name {app_name} {app_name}', hide=hide)
    cnx.run(f'rm -Rf {server_dir}', hide=hide)
    print('App running successfully')


def prepare_server_env_cmd_args(server):
    server_env_opts = ''
    server_env = server['env']
    if server_env is not None:
        for k, v in server_env.items():
            server_env_opts += f'-e {k}={v} '
    return server_env_opts


def build_docker_image(cnx, config_yaml, settings_py, hide):
    app_name = config_yaml["app"]["name"]
    unzip_dir_path = f'{server_dir}/{app_name}'
    zip_file_path = f'{server_dir}/{app_name}.zip'

    print('Uploading django project to server...')
    cnx.run(f'mkdir -p {server_dir}', hide=hide)
    cnx.run(f'rm -Rf {server_dir}/*', hide=hide)
    cnx.put(f'{app_name}.zip', server_dir)
    print('Upload complete')
    print('Preparing files...')
    cnx.run(f'unzip {zip_file_path} -d {unzip_dir_path}', hide=hide)
    append_settings_py_cmd = create_settings_cmd(config_yaml, settings_py)
    cnx.run(append_settings_py_cmd, hide=hide)
    docker_file_cmd = create_dock_file_cmd(config_yaml)
    cnx.run(docker_file_cmd, hide=hide)
    print('Building docker image...')
    cnx.run(f'docker build -t {app_name} {unzip_dir_path}', hide=hide)


def create_settings_cmd(config_yaml, settings_py):
    app_name = config_yaml["app"]["name"]
    django_app = config_yaml['app']['django_app']

    append_settings_py_cmd = f'''cat << EOF >> {server_dir}/{app_name}/{django_app}/settings.py
{settings_py}
EOF
 '''
    return append_settings_py_cmd


def create_dock_file_cmd(config_yaml):
    envs_string = ''
    for k, v in config_yaml['app']['env'].items():
        envs_string += f'ENV {k} {v}\n'

    docker_file_cmd = f'''cat << EOF > {server_dir}/{config_yaml['app']['name']}/Dockerfile
FROM {config_yaml['app']['docker']['image']}
ADD . app
RUN pip install gunicorn && pip install -r app/{config_yaml['app']['requirements_file']} || :
{envs_string}
WORKDIR /app
ENTRYPOINT [ "bash", "-c", "gunicorn {config_yaml['app']['django_app']}.wsgi -b 0.0.0.0:80" ]
EXPOSE 80
EOF
'''
    return docker_file_cmd
