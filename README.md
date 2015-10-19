GraphSpace 
================

GraphSpace is running at http://graphspace.org

Amazon EC2 Instance is running at: http://ec2-52-5-177-0.compute-1.amazonaws.com

GraphSpace has three dummy users: 

1. Username: user1@example.com Password: user1
2. Username: user2@example.com Password: user2
3. Username: user3@example.com Password: user3

Running GraphSpace on your computer
===================================

In order to get GraphSpace running on your computer, please install Python and sqlite3. We have tested GraphSpace with Python v2.7.10 and sqlite3 v3.8.10. GraphSpace does not support Python v3. The following steps describe how to install required Python packages, download the GraphSpace code, and set up and start the server.

1. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git`
2. Visit the GraphSpace directory: `cd GraphSpace`
3. Run the script to download all of the necessary dependencies. *This step may require sudo priveleges*: `python configure.py`
4. Modify gs-setup.sh file and replace all variables with appropriate values
5. Propogate changes in gs-setup.sh file to GraphSpace: `. gs-setup.sh`
  gs-setup.sh contains the following values
  * `SECRET_KEY`: key used for hashing
  * `GOOGLE_ANALYTICS_PROPERTY_ID`: ID given by Google Analytics to track users on website
  * `EMAIL_HOST`: Host provider through which email is sent (example: smtp.gmail.com)
  * `EMAIL_HOST_USER`: Email address to send emails from GraphSpace through
  * `EMAIL_HOST_PASSWORD`: Password for email address
  * `EMAIL_PORT`: Port to send emails through
6. Finally, start the GraphSpace server: `python manage.py runserver`
9. Visit `http://localhost:8080` and enjoy using GraphSpace!

Testing the GraphSpace REST API
=================================

1. Navigate to tests directory in GraphSpace: `cd tests`
2. Enter python command to run test cases: `python restapi_test.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
