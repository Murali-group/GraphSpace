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
3. Modify the `gs-setup.sh` file by populating the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` fields.  GraphSpace uses `EMAIL_HOST_USER` as the email address through which GraphSpace sends emails to its users.
4. Propogate changes to these variables in `gs-setup.sh` file to the environment: `. gs-setup.sh`.  Please run `. gs-setup.sh` and not `./gs-setup.sh` as this will not propogate the changes to the environment properly. *This step may require sudo priveleges*
5. Finally, start the GraphSpace server: `python manage.py runserver`
6. Visit `http://localhost:8080` and enjoy using GraphSpace!

Running GraphSpace on Apache
===================================

This section describes the steps required to launch GraphSpace on a server that has `apache2` running on it.  First, please follow the steps in **Running GraphSpace locally**.  Next, execute the instructions below. 

1. Visit the graphspace directory: `cd GraphSpace/graphspace`
3. In a text editor, open the file `gs-setup.sh`
4. Set `DEBUG=False` and `TEMPLATE_DEBUG=False`
5. Propogate those changes to the environment: `. gs-setup.sh`
6. Visit the `apache2` directory: `cd /path_to/apache2`. An example of the full path to this directory is `/etc/apache2`.
7. Navigate to the `sites-enabled` directory: `cd sites-enabled`
8. Create a file called `graphspace.conf`
9. Inside this file, copy and paste following lines, after replacing `path_to_GraphSpace` with the name of the directory where you downloaded GraphSpace:
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
10. Give permissions to the Apache server to access the GraphSpace database: `chmod 777 graphspace.db`
11. Navigate to the `GraphSpace/graphspace` directory and open up the file `settings.py` in a text editor
12. Replace URL_PATH with the IP address or domain name of the computer where the apache2 server is running, e.g., "http://graphspace.org/"
13. Restart the apache server. On a computer running Ubuntu, the command is `sudo service apache2 restart`

Refer to https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/ if any problems occur with the setup.

Testing the GraphSpace REST API
=================================

1. Follow the instructions above to run GraphSpace locally or on Apache2.
2. Navigate to the tests directory in GraphSpace: `cd tests`
2. Enter python command to run test cases: `python restapi_test.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
