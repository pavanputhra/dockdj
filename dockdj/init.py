import os.path
from dockdj.du_settings import CONFIG_FILE, SETTINGS_PY_FILE


INIT_YAML = '''---
server:
  host: 1.2.3.4
  # must be sudo without password
  username: root
  pem: "/home/user/.ssh/id_rsa"
app:
  # Project name used by script to name docker
  name: hello_world_stage
  settings: 'hello_world/settings.py'
  wsgi:
    app: 'hello_world.wsgi:application'
  asgi: # optional if app uses agsi like channels
    app: 'hello_world.asgi:application'
    paths: # used by nginx to route to asig
      - /ws
      - /some_thing_else
  celery: # optional for celery django app
    app: 'hello_world'
  requirements_file: 'requirements.txt'
  extra_files: # Optional: config, certs any other files loaded to /app/extra_files/* in docker container
    - /path/to/abc.txt
  # Django project directory
  path: "/path/to/django/code/hello_world"
  docker:
    image: python:3.7

compose:
  services:
    celery:
      depends_on:
        - rabbitmq
    rabbitmq:
      image: rabbitmq

'''


SETTING_PY = '''
DEBUG = False

# Add the your servers host name or ip address
ALLOWED_HOSTS = []

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'
'''


def init(verbose=False):

    if os.path.isfile(CONFIG_FILE):
        print(f'File {CONFIG_FILE} already exists.')
        return

    if os.path.isfile(SETTINGS_PY_FILE):
        print(f'File {SETTINGS_PY_FILE} already exists.')
        return

    with open(CONFIG_FILE, 'w') as the_file:
        the_file.write(INIT_YAML)

    with open(SETTINGS_PY_FILE, 'w') as the_file:
        the_file.write(SETTING_PY)
