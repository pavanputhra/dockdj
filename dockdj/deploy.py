import os
from dockdj.du_settings import CONFIG_FILE, SETTINGS_PY_FILE
from fabric import Connection
import yaml
from invoke import exceptions
import shutil

PATH_PREFIX = '/var/tmp/'


def deploy(verbose=False):
    hide = not verbose
    print('Deploying')
    if not os.path.isfile(CONFIG_FILE):
        print("Please run django_up init to create config file")
        return

    with open(CONFIG_FILE, 'r') as the_file:
        config_yaml = yaml.load(the_file)

    with open(SETTINGS_PY_FILE, 'r') as the_file:
        settings_py = the_file.read()

    print('Zipping the django project')
    app_dir = config_yaml['app']['path']
    app_name = config_yaml['app']['name']
    docker_imagedocker_image = config_yaml['app']['docker']['image']
    django_app_name = config_yaml['app']['django_app']
    requirements_file = config_yaml['app']['requirements_file']
    app_port = config_yaml['app']['port']
    envs = config_yaml['app']['env']

    server_dir = PATH_PREFIX + 'django_up'

    zip_file_name = f'{app_name}.zip'
    zip_file_path = f'{server_dir}/{zip_file_name}'
    unzip_dir_path = f'{server_dir}/{app_name}'
    shutil.make_archive(app_name, 'zip', app_dir)

    envs_string = ''
    for k, v in envs.items():
        envs_string += f'ENV {k} {v}\n'

    docker_file_cmd = f'''cat << EOF > {unzip_dir_path}/Dockerfile
FROM {docker_imagedocker_image}
ADD . app
RUN pip install gunicorn && pip install -r app/{requirements_file} || :
{envs_string}
WORKDIR /app
ENTRYPOINT [ "bash", "-c", "gunicorn {django_app_name}.wsgi -b 0.0.0.0:80" ]
EXPOSE 80
EOF
'''

    append_settings_py_cmd = f'''cat << EOF >> {unzip_dir_path}/{django_app_name}/settings.py
{settings_py}
EOF
 '''

    for server in config_yaml['servers']:
        server_env = server['env']
        server_env_opts = ''
        if server_env is not None:
            for k, v in server_env.items():
                server_env_opts += f'-e {k}={v} '
        with Connection(
                host=server['host'],
                user=server['username'],
                connect_kwargs={ 'key_filename': server['pem']}) as cnx:
            try:
                print('Uploading django project to server...')
                cnx.run(f'mkdir -p {server_dir}', hide=hide)
                cnx.run(f'rm -Rf {server_dir}/*', hide=hide)
                cnx.put(zip_file_name, server_dir)
                print('Upload complete')
                print('Preparing files...')
                cnx.run(f'unzip {zip_file_path} -d {unzip_dir_path}', hide=hide)
                cnx.run(append_settings_py_cmd, hide=hide)
                cnx.run(docker_file_cmd, hide=hide)
                print('Building docker image...')
                cnx.run(f'docker build -t {app_name} {unzip_dir_path}', hide=hide)
                try:
                    cnx.run(f'docker stop {app_name}', hide=hide)
                    cnx.run(f'docker rm {app_name}', hide=hide)
                except exceptions.UnexpectedExit:
                    pass
                print('Trying to run app in docker')
                cnx.run(f'docker run -d -p {app_port}:80 {server_env_opts} --name {app_name} {app_name}', hide=hide)
                cnx.run(f'rm -Rf {server_dir}', hide=hide)
                print('App running successfully')
            except exceptions.UnexpectedExit:
                print('Some exception')

    os.remove(zip_file_name)
