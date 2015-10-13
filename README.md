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

1. Download the script get-pip.py from https://bootstrap.pypa.io/get-pip.py and save it on your computer.
2. Navigate to where you saved this script and run `python get-pip.py`. This step installs pip (Python package installer). *This step and the next two steps may  require root privileges.*
3. To install Django, run `pip install django`
4. To install the password hashing module used by GraphSpace `pip install py-bcrypt`
5. Download the GraphSpace code by running `git clone https://github.com/Murali-group/GraphSpace.git`
6. Visit the directory where you downloaded the code. 
7. Visit the GraphSpace directory: `cd GraphSpace`
8. Change the name of startup.db to graphspace.db: `mv startup.db graphspace.db`
9. Open `graphspace/settings.py` in a text editor.
10. Update the `DB_FULL_PATH property` to point to the location of `graphspace.db`. 
11. In the current directory, run the command `python manage.py migrate`
11. Finally, start the GraphSpace server: `python manage.py runserver`
12. Visit `http://localhost:8080` and enjoy using GraphSpace!

Testing the GraphSpace REST API
=================================

To test the GraphSpace REST API, run `python test-restapi.py`

This script will test all the REST API commands supported by the GraphSpace server.  If something fails, it will display the error.
