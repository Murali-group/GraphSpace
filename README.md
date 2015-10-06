GraphSpace 
================

Graphspace is running at: http://graphspace.org

Amazon EC2 Instance is running at: http://ec2-52-5-177-0.compute-1.amazonaws.com

Pre-made user logins

Username: user1@example.com Password: user1

Username: user2@example.com Password: user2

Username: user3@example.com Password: user3

Up and Running with GraphSpace
=================================

In order to get a local working copy of GraphSpace, one must have Python (v2.7.10) running on their machine as well as sqlite3.  

Next, download the script from https://bootstrap.pypa.io/get-pip.py.  Navigate to where you downloaded this script and run: python get-pip.py

This installs pip (Python package installer).  Pip allows one to download various Python specific modules.

In order to install Django, run: pip install django

We need to install our hashing module: pip install py-bcrypt

Finally, when all the packages are installed from your computer, run: git clone https://github.com/DSin52/GraphSpace.git

This installs GraphSpace server to your current directory.

Go into the GraphSpace directory: cd GraphSpace

Change the name of startup.db to graphspace.db

Open up graphspace/settings.py

Update the following properties to the appropriate paths:

DB_FULL_PATH: "Full path to the database"
DATABASE_LOCATION = 'sqlite:///graphspace.db'

Finally, run GraphSpace: python manage.py runserver