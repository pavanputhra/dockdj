# Django Up

#### Production Quality Django Deployments

Django Up is a command line tool that allows you to deploy any [Django](https://www.djangoproject.com/) app to your own server.

This tool is inspired by [Meteor up](http://meteor-up.com/) tool which is used to deploy [Meteor.js](https://www.meteor.com/) app.

You can install and use Django Up on Linux, Mac and Windows. It can deploy to servers running Ubuntu 14 or newer.

Django Up is powered by [Docker](http://www.docker.com/), making deployment easy to manage and reducing server specific errors.


#### Requirement

This tool needs Python > 3.6


#### Usage

    $ django_up init

This will create two files `django_up.yaml` and `settings.py`

Modify the `django_up.yaml` file to enter server configuration and app details. Initial file looks as follows.

    ---
    servers:
    - host: 1.2.3.4
      # must be sudo without password
      username: root
      pem: "~/.ssh/id_rsa"
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

`settings.py` fill contains settings which will be appended to your django app's settings.py file. You can enter production related settings or override development settings here. Initial `settings.py` file looks like as follows.


    DEBUG = False

    # Add the your servers host name or ip address
    ALLOWED_HOSTS = ['1.2.3.4', 'www.example.com']


After editing these two files appropriately run following command to setup server. This will install docker in Ubuntu servers if not already installed.

    
    $ django_up setup


To deploy the django app run following.

    $ django_up deploy
    
This will create docker image of your Django app. Runs the Django app using [gunicorn](https://gunicorn.org/) and binds the port to the port specified in `django_up.yaml`.