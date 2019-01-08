import os
from settings import CONFIG_FILE
from fabric import Connection
import yaml
from invoke import exceptions
import shutil

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

    zip_file_name = app_name + '.zip'
    shutil.make_archive(app_name, 'zip', app_dir)

    server_dir = 'django_up'

    docker_file_cmd = '''cat << EOF > Dockerfile
FROM {0}
ADD . app
RUN pip install gunicorn && pip install -r app/{1} || :
WORKDIR /app
ENTRYPOINT [ "bash", "-c", "gunicorn {2}.wsgi -b 0.0.0.0:80" ]
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
                cnx.run('mkdir -p ' + server_dir)
                with cnx.cd(server_dir):
                    cnx.run('pwd')
                    cnx.put(zip_file_name, server_dir)
                    print('Upload complete')
                    cnx.run('unzip {0} -d {1}'.format(zip_file_name, app_name))
                    with cnx.cd(app_name):
                        cnx.run('touch Dockerfile')
                        cnx.run(docker_file_cmd.format(docker_imagedocker_image, requirements_file,  django_app_name))
                        cnx.run('docker build -t {0} .'.format(app_name))
                        cnx.run('docker run -d -p {0}:80 {1}'.format(app_port, app_name))
                    cnx.run('rm -R {0}'.format(app_name))
                cnx.run('rm -R {0}'.format(server_dir))
            except exceptions.UnexpectedExit:
                print('Some exception')

    os.remove(zip_file_name)
