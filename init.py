import os.path
from du_settings import CONFIG_FILE


def init():
    init_yaml = '''---
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

    if os.path.isfile(CONFIG_FILE):
        print('File {0} already exists.'.format(CONFIG_FILE))
        return

    with open(CONFIG_FILE, 'w') as the_file:
        the_file.write(init_yaml)
