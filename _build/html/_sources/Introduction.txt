Introduction to GraphSpace
====================================================
This will contain a brief overview of how the entire system of GraphSpace works for developers.

Current Location (Soon to be moved)
----------------------------------------------
The repository for GraphSpace (Python version) is currently https://github.com/DSin52/GraphSpace.git.

This is a private repository, so please ask divit52@vt.edu to add you as a collaborator or if any issues come up.

** This location will eventually get changed to Murali's Github account **

Up and Running
--------------------------------
This repository should have everything but the database.

In order to get the most current database (holmes' version: (/data/craigy/graphspace-production/graphspace-server/graphspace.db), simply cp it to directory where graphspace is running.

Next, navigate to the top-most directory of this project.

There should be a script called alter_table.py.
This script is a conversion script which changes the previous schema of GraphSpace to the new schema (retaining all data).  It has two comands, 'alter' and 'drop'.  

Invoke the following commands to create a database compatible with the new schema: 

Command to create new tables with updated schema and transfer data:

python alter_table.py graphspace.db alter

Command to delete:

python alter_table.py graphspace.db drop

You should now have a database with the updated schema.

Now, we have to sync the database with Django to construct permission tables:

python manage.py syncdb

In order to start the server, simply run: 

python manage.py runserver

It should run on port 8000 by default

**Note**

If you want to change the database name, you have to change it in the following two places:

graphs/util/db_conn.py: Change the url of the database to contain the name of the database (for example: 'sqlite:///graphspace.db')

graphs/util/db.py: change DB_NAME (for example: 'graphspace.db')

graphs/util/db_init.py: Change the following: db = Database('prod') to the file location path in db_conn.py (see above)

Using the Web Application
---------------------------------

The GraphSpace server is laid out into the following folders:

/graphs contains most of the Python code, for handling urls, database accesses, views etc.

/graphs/static/ contains CSS and JavaScript libraries.

/graphs/templates/ contains html and Django templates.

/graphs/auth/ contains codes related to authentication (user login).

/graphs/util/ contains utilities such as in-graph search, database connection, json converter, paginator etc.

/graphspace contains settings and other scripts that comes with Django.

Working on GraphSpace
-------------------------------------------

It is strongly recommended to take time to read and try the Django tutorial to grasp the usage of it. The Django version used here is 1.6.

Django Documentation
--------------------------
You will also want to get familiar with SQLALchemy, for accessing and querying from databases. GraphSpace is using SQLAlchemy version 0.9.

SQLAlchemy Documentation
---------------------------------
/graphs contains all the files necessary. To describe few important ones:

views.py - functions defined in this file model the view of the site.

urls.py - defines how the URLs are handled.

models.py - defines the database model used in GraphSpace. Due to some constrains in Django ORM, we used third party ORM called SQLALchemy.

Once you get familiar with Django by going through its tutorial and some of its documentation, you will start to see how all these files work together. I recommend to get familiar with views, templates, forms, and url handling, which can be found in the documentation. (their documentation is pretty good) You may also want to look at middleware but it is not used as extensively because we replaced Django's ORM with SQLAlchemy.

I strongly recommend to start with merging the databases, so that the GraphSpace can run on a single database instead of couple. Currently it runs on 2~3 databases, one being "test.db" to support user login, and others being the backup copy of the live database. To make database access easier, I wrote a simple module for it. It is located at /graphs/util/db_conn.py

One change I made when I implemented the database model with SQLALchemy is to rename the "id" column of every table to be "tablename_id". For example, "id" column in "user" table would be "user_id". In the live version, most tables have just "id" column. You will want to watch out for this when merging the databases. This also means that you will need to change some of the queries used in views.py and possibly in other modules to have correct column names. Most of the queries are performed on the backup version of the live database, so the queries use the column "id" instead of something like "user_id".

Many of the implemented functionality are basic. For example, when you search for a node or an edge, the search is performed on the entire database without considering permissions. Details are described in the TODO list below.
The overall look of the GraphSpace is modeled after the Perl version of the GraphSpace. If you compare them, there won't be too much of a difference.

Using the REST API
---------------------------------

In order to use the REST API, install curl (linux).  Follow the REST API section within the HELP section in GraphSpace.  If you get wierd responses, simply pipe it to a txt file for easier tracing of the logs: 

curl [command] > output.txt