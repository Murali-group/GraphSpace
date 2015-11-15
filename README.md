GraphSpace 
================

GraphSpace is running at http://graphspace.org

GraphSpace has three dummy users: 

1. Username: user1@example.com Password: user1
2. Username: user2@example.com Password: user2
3. Username: user3@example.com Password: user3

Running GraphSpace locally
===================================

Please install Python, sqlite3, and python-dev, which are pre-requisites for GraphSpace. We have tested GraphSpace with Python v2.7.10 and sqlite3 v3.8.10. GraphSpace does not support Python v3. The following steps describe how to install Python packages required by GraphSpace, download the GraphSpace code, and set up and start the server.  The following instructions should apply to computers running a version of the Linux or OS X operating systems.

1. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git`
2. Visit the GraphSpace directory: `cd GraphSpace`
3. Modify the `gs-setup.sh` file by populating `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` fields.  GraphSpace uses `EMAIL_HOST_USER` as the email address to send emails through.
4. Propogate changes to these variables in `gs-setup.sh` file to the environment: `. gs-setup.sh`. *This step may require sudo priveleges*
5. Finally, start the GraphSpace server: `python manage.py runserver`
6. Visit `http://localhost:8080` and enjoy using GraphSpace!

Running GraphSpace on Apache
===================================

This section describes the steps required to launch GraphSpace on a server that has `apache2` running on it. Please install `apache2` on your server. Before we configure GraphSpace for running on Apache, please follow the steps in **Running GraphSpace locally**.  After you have completed all the steps in this section, execute the instructions below. 

1. Visit the graphspace directory: `cd GraphSpace/graphspace`
3. In a text editor, open up `gs-setup.sh` file
4. Set `DEBUG=False` and `TEMPLATE_DEBUG=False`
5. Propogate those changes: `. gs-setup.sh`
6. Visit the `apache2` directory: `cd /path_to/apache2`. Typically the full path to this directory is `/etc/apache2`.
7. Navigate to the `sites-enabled` directory: `cd sites-enabled`
8. Create a file called `graphspace.conf`
9. Inside this file, copy and paste following lines, after replacing `path_to_GraphSpace` with the name of the directory where you downloaded GraphSpace
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
10. Save the file
11. Restart the apache server

Refer to https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/ if any problems occur with the setup.

Testing the GraphSpace REST API
=================================

1. Follow the instructions above to run GraphSpace locally or on Apache2.
2. Navigate to the tests directory in GraphSpace: `cd tests`
2. Enter python command to run test cases: `python restapi_test.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
