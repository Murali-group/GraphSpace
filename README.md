GraphSpace 
================

GraphSpace is running at http://graphspace.org

GraphSpace has three dummy users: 

1. Username: user1@example.com Password: user1
2. Username: user2@example.com Password: user2
3. Username: user3@example.com Password: user3

Requirements
===================================
1. Python v2.7.10
2. [postgreSQL](https://github.com/Murali-group/GraphSpace/wiki/PostgreSQL-Installation)
3. virtualenv
4. [bower](https://bower.io/)
5. [ElasticSearch](https://github.com/Murali-group/GraphSpace/wiki/Steps-for-setting-up-ElasticSearch-on-AWS)

Running GraphSpace locally
===================================

In order to run GraphSpace, please install postgreSQL and both the Python runtime and development environments. We have tested GraphSpace with Python v2.7.10 and postgreSQL v9.6.2. GraphSpace does not support Python v3. GraphSpace performs best on either Mozilla Firefox or Google Chrome browsers. The following steps describe how to install Python packages required by GraphSpace, download the GraphSpace code, and set up and start the server.  The following instructions should apply to computers running a version of the Linux or OS X operating systems.

1. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git` or by downloading the latest release: https://github.com/Murali-group/GraphSpace/releases.
2. Visit the GraphSpace directory: `cd GraphSpace`
3. Create a virtual environment for the project: `virtualenv venv`
4. Start using the virtual environment: `source venv/bin/activate`
5. In `/graphspace/settings/local.py` file, change the postgres user credentials:
   ```
   DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': <database name>,
            'USER': <user name>,
            'PASSWORD': <password (if any)>,
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
   ```
6. Install graphspace: `sh install.sh`
7. Finally, start the GraphSpace server: `python manage.py runserver --settings=graphspace.settings.local`
8. Visit `http://localhost:8080` and enjoy using GraphSpace!

Running GraphSpace on Apache
===================================

This section describes the steps required to launch GraphSpace on a server that has `apache2` running on it.  First, please follow the steps in **Running GraphSpace locally**.  Next, execute the instructions below. 

1. Follow instructions 1-5 in `Running GraphSpace locally`
2. Add settings file `production.py` by copying local settings file. `cp graphspace/settings/local.py graphspace/settings/`
3. Update your `production.py` settings file.
  1. InSet `URL_PATH` to the URL where your server will be running.  *Note: Please add the ending '/' character at the end of this value: For example: http://graphspace.org/*
  2. Modify the `PATH` to point to where GraphSpace directory exists.  *Note: Please add the ending '/' character at the end of this value: For example: /home/ubuntu/GraphSpace/*
4. Visit the `apache2` directory: `cd /path_to/apache2`. An example of the full path to this directory is `/etc/apache2`.
5. Navigate to the `sites-enabled` directory: `cd sites-enabled`
6. Create a file called `graphspace.conf` and access this file using admin privileges: `sudo vim graphspace.conf'
7. Inside this file, copy and paste following lines, after replacing `path_to_GraphSpace` with the name of the directory where you downloaded GraphSpace:

 ```
WSGIDaemonProcess GraphSpace python-path=/path_to_GraphSpace:/path_to_GraphSpace/venv/lib/python2.7/site-packages/ python-eggs=/path_to_python_eggs
WSGIProcessGroup GraphSpace
WSGIScriptAlias / /path_to_GraphSpace/graphspace/wsgi.py

  <Directory /path_to_GraphSpace/graphspace/>
     <Files wsgi.py>
         Order deny,allow
         Require all granted
     </Files>
  </Directory>
  
  Alias /static/ /path_to_GraphSpace/static/
  
  <Directory /path_to_GraphSpace/static/>
      Require all granted
  </Directory>
  
  <Directory /path_to_GraphSpace>
   Options Indexes FollowSymLinks
   AllowOverride None
   Require all granted
  </Directory>
 ```
 
8. Install module to recognize Django application through apache2: `sudo apt-get install libapache2-mod-wsgi`
9. Give permission to access static files through apache2.  Navigate outside GraphSpace and type: `chmod 777 GraphSpace`
10. Create a directory for python-eggs. `mkdir /path_to_python_eggs`
11. Give permission to access static files through apache2. `chmod 777 /path_to_python_eggs`
12. Restart the apache server. On a computer running Ubuntu, the command is `sudo service apache2 restart`

Refer to https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/ if any problems occur with the setup.


Contributing
=================

Feel free to fork and send us pull requests. Here are the [guidelines for contribution](https://github.com/Murali-group/GraphSpace/blob/master/CONTRIBUTING.md) in GraphSpace.
