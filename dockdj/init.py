import os.path
from dockdj.du_settings import CONFIG_FILE, SETTINGS_PY_FILE


INIT_YAML = '''---
servers:
- host: 1.2.3.4
  # must be sudo without password
  username: root
  pem: "/home/user/.ssh/id_rsa"
  # optional
  env:
    PER_SERVER: abc
app:
  # Any name used by script to name docker
  name: abc
  # Django app dir which contains wsgi.py and settings.py
  django_app: 'hello_world'
  requirements_file: 'requirements.txt'
  port: 80
  # Django app dir which contains wsgi.py and settings.py
  path: "/path/to/project"
  docker:
    image: python:3.7
  env:
    FOO: foo
    BAR: bar
'''


SETTING_PY = '''
DEBUG = False

# Add the your servers host name or ip address
ALLOWED_HOSTS = []
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
