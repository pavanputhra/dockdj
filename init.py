import os.path
from settings import CONFIG_FILE


def init():
    init_yaml = '''---
servers:
- host: 1.2.3.4
  username: root
  pem: "~/.ssh/id_rsa"
  env: {}
app:
  name: abc
  django_app: ''
  path: "../"
  docker:
    image: abernix/meteord:base
  env:
    ROOT_URL: http://app.com
    MONGO_URL: mongodb://localhost/meteor
'''

    if os.path.isfile(CONFIG_FILE):
        print('File {0} already exists.'.format(CONFIG_FILE))
        return

    with open(CONFIG_FILE, 'w') as the_file:
        the_file.write(init_yaml)
