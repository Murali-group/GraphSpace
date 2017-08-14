GraphSpace 
================

GraphSpace is running at http://graphspace.org

GraphSpace has three dummy users: 

1. Username: user1@example.com Password: user1
2. Username: user2@example.com Password: user2
3. Username: user3@example.com Password: user3

Requirements
===================================

1. [Python](https://askubuntu.com/a/101595) v2.7.10
2. [postgreSQL](https://github.com/Murali-group/GraphSpace/wiki/PostgreSQL-Installation) with pg_trgm extension
3. [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
4. [bower](https://bower.io/) _dependant on [Node.js](https://github.com/Murali-group/GraphSpace/wiki/Install-Node.js)_
5. [Apache Kafka](https://github.com/Murali-group/GraphSpace/wiki/Install-Apache-Kafka)
6. [ElasticSearch](https://github.com/Murali-group/GraphSpace/wiki/Steps-for-setting-up-ElasticSearch-on-AWS)
7. [Redis](https://github.com/Murali-group/GraphSpace/wiki/Install-Redis)
8. [Supervisor](http://supervisord.org/installing.html#installing-via-pip)

Running GraphSpace locally
===================================

In order to run GraphSpace, please install postgreSQL and both the Python runtime and development environments. We have tested GraphSpace with Python v2.7.10 and postgreSQL v9.6.2. GraphSpace does not support Python v3. GraphSpace performs best on either Mozilla Firefox or Google Chrome browsers. The following steps describe how to install Python packages required by GraphSpace, download the GraphSpace code, and set up and start the server.  The following instructions should apply to computers running a version of the Linux or OS X operating systems.

1. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git` or by downloading the latest release: https://github.com/Murali-group/GraphSpace/releases.
2. Visit the GraphSpace directory: `cd GraphSpace`
3. Create a virtual environment for the project: `virtualenv venv`
4. Start using the virtual environment: `source venv/bin/activate`
5. Install graphspace: `sh install.sh`
   
   _Note : While installing psycopg2, you might encounter 
   [```Error: You need to install postgresql-server-dev-X.Y for building a server-side extension or libpq-dev for building a client-side application.```](https://stackoverflow.com/q/28253681/4646197)
   To fix it follow the solution given [here](https://stackoverflow.com/a/28254860/4646197)._
6. Finally, start the GraphSpace server: `python manage.py runserver --settings=graphspace.settings.local`
7. Visit `http://localhost:8080` and enjoy using GraphSpace!

Running GraphSpace on Apache
===================================

This section describes the steps required to launch GraphSpace on a server that has `apache2` running on it.  First, please follow the steps in **Running GraphSpace locally**.  Next, execute the instructions below. 

1. Follow instructions 1-5 in `Running GraphSpace locally`
2. Add settings file `production.py` by copying local settings file. `cp graphspace/settings/local.py graphspace/settings/`
3. Update your `production.py` settings file.
   1. InSet `URL_PATH` to the URL where your server will be running.  *Note: Please add the ending '/' character at the end of this value: For example: http://graphspace.org/*
   2. Modify the `PATH` to point to where GraphSpace directory exists.  *Note: Please add the ending '/' character at the end of this value: For example: /home/ubuntu/GraphSpace/*
4. Update location of graphspace directory (`GRAPHSPACE`) in `runworker` and `daphne` file.
5. When Supervisor is installed you can give it programs to start and watch by creating configuration files in the `/etc/supervisor/conf.d` directory. For Daphne and workers we’ll create a file named `/etc/supervisor/conf.d/graphspace.conf` with the following content, after replacing `path_to_GraphSpace` with the name of the directory where you downloaded GraphSpace, `path_to_kafka` with the name of the directory where you downloaded Kafka and `user_name` with the name of the current user:

   ```
   [program:daphne_graphspace]
   command=sh /path_to_GraphSpace/daphne
   user = user_name
   stdout_logfile = /path_to_GraphSpace/logs/daphne.log
   redirect_stderr = true
   environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8,PYTHON_EGG_CACHE="/home/melvin15may/GraphSpace/python-eggs"
   priority=2

   [program:runworker_daphne_graphspace]
   command=sh /path_to_GraphSpace/runworker
   process_name=%(process_num)s
   numprocs = 2
   user = user_name
   stdout_logfile = /path_to_GraphSpace/logs/runworker.log
   redirect_stderr = true
   environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8,PYTHON_EGG_CACHE="/home/melvin15may/GraphSpace/python-eggs"
   priority=3

   [program:kafka_graphspace]
   command=/path_to_kafka/bin/kafka-server-start.sh /path_to/kafka/config/server.properties
   user = user_name
   stdout_logfile = /path_to_GraphSpace/logs/kafka.log
   redirect_stderr = true
   environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8
   priority=1
   ```
6. Update settings and run supervisord:
   ```
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl restart all
   ```   
7. Visit the `apache2` directory: `cd /path_to/apache2`. An example of the full path to this directory is `/etc/apache2`.
8. Navigate to the `sites-enabled` directory: `cd sites-enabled`
9. Create a file called `graphspace.conf` and access this file using admin privileges: `sudo vim graphspace.conf'
10. Inside this file, copy and paste following lines, after replacing `path_to_GraphSpace` with the name of the directory where you downloaded GraphSpace and `path_to_python_eggs` with the name of the directory where you wish to put the python files:

    ```
    WSGIDaemonProcess GraphSpace python-path=/path_to_GraphSpace:/path_to_GraphSpace/venv/lib/python2.7/site-packages/ python-eggs=/path_to_python_eggs
    WSGIProcessGroup GraphSpace
    WSGIScriptAlias / /path_to_GraphSpace/graphspace/wsgi.py
    
    WSGIApplicationGroup %{GLOBAL}
    
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
11. Install module to recognize Django application through apache2: `sudo apt-get install libapache2-mod-wsgi`
12. Give permission to access static files through apache2.  Navigate outside GraphSpace and type: `chmod 777 GraphSpace`
13. Create a directory for python-eggs. `mkdir /path_to_python_eggs`
14. Give permission to access python-egg files through apache2. `chmod 777 /path_to_python_eggs`
15. Run the following cmd: ``` a2enmod rewrite ```, ``` a2enmod proxy ``` and ``` a2enmod proxy_wstunnel ```
16. Inside the `/path_to/apache2/sites-enabled/000-default.conf`, copy and paste following lines inside ``` <VirtualHost *:80> </VirtualHost> ```
    ```
    RewriteEngine on
    RewriteCond %{HTTP:UPGRADE} ^WebSocket$ [NC,OR]
    RewriteCond %{HTTP:CONNECTION} ^Upgrade$ [NC]
    RewriteRule .* ws://127.0.0.1:9099%{REQUEST_URI} [P,QSA,L]
    ```
17. Restart the apache server. On a computer running Ubuntu, the command is `sudo service apache2 restart`

Refer to https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/ if any problems occur with the setup.


Contributing
=================

Feel free to fork and send us pull requests. Here are the [guidelines for contribution](https://github.com/Murali-group/GraphSpace/blob/master/CONTRIBUTING.md) in GraphSpace.
