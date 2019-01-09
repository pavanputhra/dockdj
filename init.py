import os.path
from du_settings import CONFIG_FILE, SETTINGS_PY_FILE


INIT_YAML = '''---
servers:
- host: 1.2.3.4
  username: root
  pem: "~/.ssh/id_rsa"
  env: {}
app:
  name: abc
  django_app: 'hello_world'
  requirements_file: 'requirements.txt'
  port: 80
  path: "/path/to/project"
  docker:
    image: python:3.7
  env:
    FOO: http://app.com
    BAR: mongodb://localhost/meteor
'''


SETTING_PY = '''
DEBUG = False

# Add the your servers host name or ip address
ALLOWED_HOSTS = []
'''


def init():

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
