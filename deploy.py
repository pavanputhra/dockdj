import os
from du_settings import CONFIG_FILE
from fabric import Connection
import yaml
from invoke import exceptions
import shutil

PATH_PREFIX = '/var/tmp/'


def deploy():
    print('Deploying')
    if not os.path.isfile(CONFIG_FILE):
        print("Please run django_up init to create config file")
        return

    with open(CONFIG_FILE, 'r') as the_file:
        config_yaml = yaml.load(the_file)

    print('Zipping the django project')
    app_dir = config_yaml['app']['path']
    app_name = config_yaml['app']['name']
    docker_imagedocker_image = config_yaml['app']['docker']['image']
    django_app_name = config_yaml['app']['django_app']
    requirements_file = config_yaml['app']['requirements_file']
    app_port = config_yaml['app']['port']

    server_dir = PATH_PREFIX + 'django_up'

    zip_file_name = f'{app_name}.zip'
    zip_file_path = f'{server_dir}/{zip_file_name}'
    unzip_dir_path = f'{server_dir}/{app_name}'
    shutil.make_archive(app_name, 'zip', app_dir)

    docker_file_cmd = f'''cat << EOF > {unzip_dir_path}/Dockerfile
FROM {docker_imagedocker_image}
ADD . app
RUN pip install gunicorn && pip install -r app/{requirements_file} || :
WORKDIR /app
ENTRYPOINT [ "bash", "-c", "gunicorn {django_app_name}.wsgi -b 0.0.0.0:80" ]
EXPOSE 80
EOF
'''

    for server in config_yaml['servers']:
        with Connection(
                host=server['host'],
                user=server['username'],
                connect_kwargs={ 'key_filename': server['pem']}) as cnx:
            try:
                print('Uploading django project to server.')
                cnx.run(f'mkdir -p {server_dir}')
                cnx.run(f'rm -Rf {server_dir}/*')
                cnx.put(zip_file_name, server_dir)
                print('Upload complete')
                cnx.run(f'unzip {zip_file_path} -d {unzip_dir_path}')
                cnx.run(docker_file_cmd)
                cnx.run(f'docker build -t {app_name} {unzip_dir_path}')
                cnx.run(f'docker run -d -p {app_port}:80 {app_name}')
                cnx.run('rm -Rf {0}'.format(server_dir))
            except exceptions.UnexpectedExit:
                print('Some exception')

    os.remove(zip_file_name)
