GraphSpace 
================

Graphspace is running at: http://graphspace.org

Amazon EC2 Instance is running at: http://ec2-52-5-177-0.compute-1.amazonaws.com

Pre-made user logins

user1@example.com user1
user2@example.com user2
user3@example.com user3

Up and Running with GraphSpace
=================================

In order to get a local working copy of GraphSpace, one must have Python (v2.7.10) running on their machine as well as sqlite3.  

Next, download the script from https://bootstrap.pypa.io/get-pip.py.  Navigate to where you downloaded this script and run: python get-pip.py

This installs pip (Python package installer).  Pip allows one to download various Python specific modules.

In order to install Django, run: pip install django

We need to install our hashing module: pip install py-bcrypt

Install SQLAlchemy: pip install sqlalchemy

Finally, when all the packages are installed from your computer, run: git clone https://github.com/DSin52/GraphSpace.git

This installs GraphSpace module to your current directory.

Go into the GraphSpace directory: cd GraphSpace

Run GraphSpace: python manage.py runserver