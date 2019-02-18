import io
import os

import jinja2
import yaml

from dockdj.util import read_config_files
from fabric import Connection
from invoke import exceptions
import shutil
from importlib import resources
from string import Template

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
            pass
            # build_docker_image(cnx, config_yaml, settings_py, hide)
            # server_env_opts = prepare_server_env_cmd_args(server)
            # cmd_args = ' '.join(args)
            # manage_cmd = f'python manage.py {cmd_args}'
            # print(manage_cmd)
            # cnx.run(
            #     f'docker run {server_env_opts} --entrypoint "/bin/bash" {app_name} -c "{manage_cmd}"')
            # cnx.run(f'rm -Rf {server_dir}', hide=hide)
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
                connect_kwargs={'key_filename': server['pem']}) as cnx:
            try:
                prepare_dir_structs(cnx, config_yaml, settings_py, hide)
                run_docker_app(cnx, config_yaml, server, hide)

            except exceptions.UnexpectedExit as e:
                print('Some exception')
                print(e)

    os.remove(f'{app_name}.zip')


def prepare_dir_structs(cnx, config_yaml, settings_py, hide):
    app_name = config_yaml["app"]["name"]
    unzip_dir_path = f'{server_dir}/{app_name}'
    zip_file_path = f'{server_dir}/{app_name}.zip'
    settings_path_rel = config_yaml["app"]["settings"]

    print('Uploading django project to server...')
    cnx.run(f'mkdir -p {server_dir}', hide=hide)
    cnx.run(f'rm -Rf {server_dir}/*', hide=hide)
    cnx.put(f'{app_name}.zip', server_dir)
    print('Upload complete')

    print('Preparing files...')

    cnx.run(f'mkdir -p {unzip_dir_path}/app', hide=hide)
    cnx.run(f'unzip {zip_file_path} -d {unzip_dir_path}/app', hide=hide)
    append_settings_py_cmd = create_settings_cmd(f'{unzip_dir_path}/app/{settings_path_rel}', settings_py)
    cnx.run(append_settings_py_cmd, hide=hide)

    docker_file_cmd = create_dock_file_cmd(config_yaml)
    cnx.run(docker_file_cmd, hide=hide)
    with cnx.cd(f'{unzip_dir_path}/app'):
        cnx.run(f'docker build -t {app_name} .', hide=hide)

    cnx.run(f'mkdir -p {unzip_dir_path}/nginx/static')
    cnx.run(f'docker run --volume {unzip_dir_path}/nginx/static:/static --workdir /app {app_name} python manage.py collectstatic --noinput')

    create_nginx_cmd = create_nginx_site_file(config_yaml)
    cnx.run(create_nginx_cmd, hide=hide)
    nginx_docker = resources.read_text("dockdj", "nginx_docker.txt")
    nginx_docker_io = io.StringIO(nginx_docker)
    nginx_docker_io.name = 'Dockerfile'
    cnx.put(nginx_docker_io, f'{server_dir}/{app_name}/nginx/')
    with cnx.cd(f'{unzip_dir_path}/nginx'):
        cnx.run(f'docker build -t {app_name}_nginx .', hide=hide)

    compose_dict = create_compose_dict(config_yaml)
    compose_string = yaml.dump(compose_dict, default_flow_style=False)
    compose_file = io.StringIO(compose_string)
    compose_file.name = 'docker-compose.yaml'
    cnx.put(compose_file, unzip_dir_path)


def run_docker_app(cnx, config_yaml, server, hide):
    app_name = config_yaml["app"]["name"]

    with cnx.cd(f'{server_dir}/{app_name}'):
        cnx.run('docker-compose up -d')
    print('App running successfully')


def create_settings_cmd(settings_path, settings_py):

    append_settings_py_cmd = f'''cat << EOF >> {settings_path}
{settings_py}
STATIC_ROOT = '../static'
EOF
 '''
    return append_settings_py_cmd


def create_nginx_site_file(config_yaml):
    app_name = config_yaml["app"]["name"]
    wsgi = config_yaml["app"].get('wsgi', None)
    asgi = config_yaml["app"].get('asgi', None)
    asgi_paths = config_yaml["app"]['asgi'].get('paths', []) if asgi else []
    nginx_cmd = f'cat <<-"EOF" > {server_dir}/{app_name}/nginx/default\n'
    nginx_config_temp = resources.read_text("dockdj", "nginx.jinja")
    nginx_template = jinja2.Template(nginx_config_temp)
    nginx_config = nginx_template.render(wsgi=wsgi, asgi=asgi, asgi_paths=asgi_paths)
    nginx_cmd += f'{nginx_config}\nEOF\n'
    return nginx_cmd


def create_dock_file_cmd(config_yaml):
    docker_image = config_yaml['app']['docker']['image']
    req_file = config_yaml['app']['requirements_file']
    app_name = config_yaml['app']['name']

    temp_data = {
        'docker_image': docker_image,
        'req_file': req_file,
    }

    docker_template = resources.read_text("dockdj", "docker.txt")
    temp = Template(docker_template)
    docker_file_data = temp.substitute(temp_data)

    docker_file_cmd = f'cat << EOF > {server_dir}/{app_name}/app/Dockerfile\n{docker_file_data}\nEOF'
    return docker_file_cmd


def create_compose_dict(config_yaml):
    app_name = config_yaml['app']['name']
    compose_dict = {
        'version': '3',
        'services': {
            'nginx': {
                'image': f'{app_name}_nginx',
                'depends_on': [],
                'ports': ["8000:80"]
            }
        }
    }

    wsgi = config_yaml['app'].get('wsgi', None)
    asgi = config_yaml['app'].get('asgi', None)
    celery = config_yaml['app'].get('celery', None)

    if wsgi:
        wsgi_app = wsgi['app']
        compose_dict['services']['wsgi'] = {
            'image': app_name,
            'command': f'gunicorn {wsgi_app} -b 0.0.0.0:80'
        }

        compose_dict['services']['nginx']['depends_on'].append('wsgi')

    if asgi:
        asgi_app = asgi['app']
        compose_dict['services']['asgi'] = {
            'image': app_name,
            'command': f'daphne -b 0.0.0.0 -p 80 {asgi_app}'
        }

        compose_dict['services']['nginx']['depends_on'].append('asgi')

    if celery:
        celery_app = celery['app']
        compose_dict['services']['celery'] = {
            'image': app_name,
            'command': f'celery worker -A {celery_app} -l info'
        }

        compose_dict['services']['nginx']['depends_on'].append('celery')

    # append service from yaml
    services = config_yaml['compose'].get('services', None)
    if services:
        service_names = services.keys()
        for name in service_names:

            if name in ['wsgi', 'asgi', 'nginx', 'celery']:
                temp_image = compose_dict['services'][name]['image']
                new_dict = services.get(name, {})
                compose_dict['services'][name].update(new_dict)
                compose_dict['services'][name]['image'] = temp_image
                continue

            compose_dict['services'][name] = services.get(name)

    return compose_dict

