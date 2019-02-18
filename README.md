# Dockdj

#### Django app deployment made easy

Dockdj is a command line tool that allows you to deploy any [Django](https://www.djangoproject.com/) app to single Ubuntu server.

This tool is inspired by [Meteor up](http://meteor-up.com/) tool which is used to deploy [Meteor.js](https://www.meteor.com/) app.

You can install and use Dockdj on Linux, Mac and Windows. It can deploy to servers running latest Ubuntu.

Dockdj is powered by [Docker compose](https://docs.docker.com/compose/overview/), making deployment easy to manage.


#### Requirement

This tool needs Python > 3.6

#### Install

Install the dockdj using following command

    $ pip install dockdj


#### Usage

Lets say you have a Django project with channels (asgi) and celery worker. 
And celery worker needs rabbit mq.
Dockdj can help to deploy this app easily with following architecture.
Each box inside server is docker container.
               
    +-----------------------------------------------------------------------------+
    |                      Ubuntu server 18.04 LTS                                |
    |                                                                             |
    |                                                   +----------------+        |
    |                                          +--------+   wsgi:80      |        |
    |        +---------------+                 |        |  (gunicorn)    |        |
    |        |  nginx:80     +-----------------+        +----------------+        |
    |        |  static files +-----------------+                                  |
    |        +---------------+                 |                                  |
    |           localhost:8000                 |        +----------------+        |
    |                                          |        |   asgi:80      |        |
    |                                          +--------+  (daphne)      |        |
    |                                                   +----------------+        |
    |                                                                             |
    |                                                                             |
    |                                                                             |
    |                                                                             |
    |                                                                             |
    |                                                                             |
    |         +--------------+                          +----------------+        |
    |         |  celery      +--------------------------+   rabbit mq    |        |
    |         |              |                          |                |        |
    |         +--------------+                          +----------------+        |
    |                                                                             |
    |                                                                             |
    |             Example deployment of django app using dockdj                   |
    +-----------------------------------------------------------------------------+

###### How to deploy as show in diagram?

Create a sibling to the django project directory for saving dockdj settings 
files which will be used to deploy the django app

    $ mkdir deploy
        
    parent
        - hello_world
        |    -hello_world
        |        -wsgi.py
        - deploy
    
    $ cd deploy

    $ dockdj init

This will create two files `dockdj.yaml` and `settings.py`

    parent
        - hello_world
        |    -hello_world
        |        -wsgi.py
        - deploy
            - dockdj.yaml
            - settings.py

Modify the `dockdj.yaml` file to enter server configuration and app details. 
Initial file looks as follows. 
Remove the optional/unused configuration according to your needs.

    ---
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


`settings.py` fill contains settings which will be appended to your django app's settings.py file. You can enter production related settings or override development settings here. Initial `settings.py` file looks like as follows.


    DEBUG = False
    
    # Add the your servers host name or ip address
    ALLOWED_HOSTS = ['1.2.3.4', 'www.example.com']
    
    CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'


After editing these two files appropriately run following command to setup server. This will install docker in Ubuntu servers if not already installed.

    
    $ dockdj setup


To deploy the django app run following.

    $ dockdj deploy
    
This will create docker images of your Django app.
Collects the static file and adds it to nginx container. 
Runs all required containers as specified in `dockdj.yaml`.
Binds the port 80 of nginx container to port 8000 of Ubuntu host. 
Port binding can be modified by adding following configuration in `dockdj.yaml'
    
    compose:
      services:
        nginx:
          ports:
          - 8004:80



#### dockdj stop

Run following command to stop all containers

    $ dockdj stop
    
    
#### dockdj restart

Run following command to restart all containers

    $ dockdj restart
    
   
#### dockdj logs

Run following command to see logs of all containers

    $ dockdj logs
    

#### dockdj one-off
    
You can run one-off script on server using one-off sub command as follows.

    $ dockdj one-off python manage.py migrate
    
 