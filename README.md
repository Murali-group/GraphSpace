GraphSpace 
================

GraphSpace is running at http://graphspace.org

GraphSpace has three dummy users: 

1. Username: user1@example.com Password: user1
2. Username: user2@example.com Password: user2
3. Username: user3@example.com Password: user3

Running GraphSpace locally
===================================

In order to get GraphSpace running on your computer, please install Python and sqlite3. We have tested GraphSpace with Python v2.7.10 and sqlite3 v3.8.10. GraphSpace does not support Python v3. The following steps describe how to install required Python packages, download the GraphSpace code, and set up and start the server.  The following instructions are for machines running Linux.

1. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git`
2. Visit the GraphSpace directory: `cd GraphSpace`
3. Run the script to download all of the necessary dependencies. *This step may require sudo priveleges*: `python configure.py`
4. Modify gs-setup.sh file and replace all variables with appropriate values
5. Propogate changes in gs-setup.sh file to GraphSpace: `. gs-setup.sh`
  * `SECRET_KEY`: key used for hashing (https://docs.djangoproject.com/en/1.8/ref/settings/#secret-key)
  * `GOOGLE_ANALYTICS_PROPERTY_ID`: Tracking ID given by Google Analytics to track GraphSpace users (https://support.google.com/analytics/answer/1032385?hl=en)
  * `EMAIL_HOST`: Host provider through which email is sent (example: smtp.gmail.com)
  * `EMAIL_HOST_USER`: Email address to send emails from GraphSpace through
  * `EMAIL_HOST_PASSWORD`: Password for email address
  * `EMAIL_PORT`: Port to send emails through
6. Finally, start the GraphSpace server: `python manage.py runserver`
9. Visit `http://localhost:8080` and enjoy using GraphSpace!

Running GraphSpace on Apache
===================================

This section describes the steps required to launch GraphSpace on a server that has `apache2` running on it.  Before we configure GraphSpace for running on Apache, please follow the steps in **Running GraphSpace locally section**.  After you have completed all the steps in the previous section, execute the instructions below. 

1. Visit the GraphSpace directory: `cd GraphSpace`
2. Navigate to graphspace directory: `cd graphspace`
3. In a text editor, open up settings.py
4. In settings.py, set `DEBUG=False` and `TEMPLATE_DEBUG=False`
5. Next, we need to install apache2 on our server: `sudo apt-get install apache2`
6. Visit `apache2` directory
7. Navigate to `sites-enabled` directory: `cd sites-enabled`
8. Create a file called `graphspace.conf`
9. Inside file, copy and paste following lines
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
11. Restart apache server

Refer to https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/ if any problems occur with the setup.

Testing the GraphSpace REST API
=================================

1. Navigate to tests directory in GraphSpace: `cd tests`
2. Enter python command to run test cases: `python restapi_test.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
