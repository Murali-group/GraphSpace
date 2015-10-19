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
3. Open `graphspace/settings.py` in a text editor.
4. Update the `DB_FULL_PATH property` to point to the location of `graphspace.db`. 
5. Run the script to download all of the necessary dependencies *May require sudo priveleges* `python configure.py`
6. Modify gs-setup.sh file and replace all variables with appropriate values
7. Propogate changes in gs-setup.sh file to GraphSpace: `. gs-setup.sh`
8. Finally, start the GraphSpace server: `python manage.py runserver`
9. Visit `http://localhost:8080` and enjoy using GraphSpace!

Testing the GraphSpace REST API
=================================

1. Navigate to tests directory in GraphSpace: `cd tests`
2. Enter python command to run test cases: `python restapi_test.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
