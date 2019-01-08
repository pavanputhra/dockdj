import os.path


def init():
    init_json = '''{
   "servers":{
      "one":{
         "host":"1.2.3.4",
         "username":"root",
         "pem":"~/.ssh/id_rsa",
         "env": {
            
         }
      }
   },
   "app":{
      "name":"abc",
      "django_app": "",
      "path":"../",
      "docker":{
         "image":"abernix/meteord:base"
      },
      "env":{
         "ROOT_URL":"http://app.com",
         "MONGO_URL":"mongodb://localhost/meteor"
      }
   }
}
'''
    filename = 'django_up.json'

    if os.path.isfile(filename):
        print('File {0} already exists.'.format(filename))

    with open(filename, 'w') as the_file:
        the_file.write(init_json)
