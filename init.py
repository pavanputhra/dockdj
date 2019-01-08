import os.path


def init():
    init_yaml = '''---
servers:
  one:
    host: 1.2.3.4
    username: root
app:
  name: app
  path: "./"
  servers:
    one: {}
  buildOptions:
    serverOnly: true
  env:
    ROOT_URL: http://app.com
    MONGO_URL: mongodb://mongodb/meteor
    MONGO_OPLOG_URL: mongodb://mongodb/local
  docker:
    image: abernix/meteord:node-8.4.0-base
  enableUploadProgressBar: true
'''
    filename = 'django_up.yaml'

    if os.path.isfile(filename):
        print('File django_up.yaml already exists.')

    with open(filename, 'w') as the_file:
        the_file.write(init_yaml)
