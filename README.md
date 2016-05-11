GraphSpace 
================

GraphSpace is running at http://graphspace.org

GraphSpace has three dummy users: 

1. Username: user1@example.com Password: user1
2. Username: user2@example.com Password: user2
3. Username: user3@example.com Password: user3

Running GraphSpace locally
===================================

In order to run GraphSpace, please install sqlite3 and both the Python runtime and development environments. We have tested GraphSpace with Python v2.7.10 and sqlite3 v3.8.10. GraphSpace does not support Python v3. GraphSpace performs best on either Mozilla Firefox or Google Chrome browsers. The following steps describe how to install Python packages required by GraphSpace, download the GraphSpace code, and set up and start the server.  The following instructions should apply to computers running a version of the Linux or OS X operating systems.

1. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git` or by downloading the latest release: https://github.com/Murali-group/GraphSpace/releases.
2. Visit the GraphSpace directory: `cd GraphSpace`
3. Modify the `local_settings.py` file by populating the `EMAIL_HOST`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD` fields.  GraphSpace uses `EMAIL_HOST_USER` as the email address through which GraphSpace sends emails to its users.  `EMAIL_HOST` is the email protocol to use.  For example, `smtp.gmail.com` would be used if using a Gmail email address.
4. Install all the necessary packages that GraphSpace requires: `python local_settings.py`*This step may require sudo privileges*
5. Finally, start the GraphSpace server: `python manage.py runserver`
6. Visit `http://localhost:8080` and enjoy using GraphSpace!

Running GraphSpace on Apache
===================================

This section describes the steps required to launch GraphSpace on a server that has `apache2` running on it.  First, please follow the steps in **Running GraphSpace locally**.  Next, execute the instructions below. 

1. Follow instructions 1-5 in `Running GraphSpace locally` 
EMAIL_HOST_PASSWORD` fields.
2. Set `URL_PATH` to the URL where your server will be running.  *Note: Please add the ending '/' character at the end of this value: For example: http://graphspace.org/*
3. Visit the `apache2` directory: `cd /path_to/apache2`. An example of the full path to this directory is `/etc/apache2`.
4. Navigate to the `sites-enabled` directory: `cd sites-enabled`
5. Create a file called `graphspace.conf` and access this file using admin privileges: `sudo vim graphspace.conf'
6. Inside this file, copy and paste following lines, after replacing `path_to_GraphSpace` with the name of the directory where you downloaded GraphSpace:
 ```
 WSGIScriptAlias / /path_to_GraphSpace/graphspace/wsgi.py
 WSGIPythonPath /path_to_GraphSpace
  <Directory /path_to_GraphSpace/graphspace>
     <Files wsgi.py>
         Order deny,allow
         Require all granted
     </Files>
  </Directory>
  
  Alias /static/ /path_to_GraphSpace/graphspace/graphs/static/
  
  <Directory /path_to_GraphSpace/graphspace/graphs/static>
      Require all granted
  </Directory>
  
  <Directory /path_to_GraphSpace>
   Options Indexes FollowSymLinks
   AllowOverride None
   Require all granted
  </Directory>
 ```
7. Give permissions to the Apache server to access the GraphSpace database: `chmod 777 graphspace.db`
8. Install module to recognize Django application through apache2: `sudo apt-get install libapache2-mod-wsgi'
9. Give permission to access static files through apache2.  Navigate outside GraphSpace and type: `chmod 777 GraphSpace`
10. Restart the apache server. On a computer running Ubuntu, the command is `sudo service apache2 restart`

Refer to https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/ if any problems occur with the setup.

Testing the GraphSpace REST API
=================================

1. Follow the instructions above to run GraphSpace locally or on Apache2.
2. Navigate to the tests directory in GraphSpace: `cd tests`
2. Enter python command to run test cases: `python restapi_test.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
