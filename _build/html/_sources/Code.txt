Source Code Structure
======================================

views.py
--------------------------------------
Contains all of the routing methods for 
incoming requests.  Located at GraphSpace/graphs/views.py

.. automodule:: graphs.views
   :members:

urls.py
--------------------------------------
Handles all incoming URL's and directs them to proper method in views.py.
Located at GraphSpace/graphs/urls.py

models.py
--------------------------------------
Contains the model that Django uses to communicate with database. Located at GraphSpace/graphs/models.py

.. automodule:: graphs.models
   :members:

forms.py
--------------------------------------
Pre-made HTML forms to send to the front-end. Located at GraphSpace/graphs/forms.py

.. automodule:: graphs.forms
	:members:

Utils - db.py
--------------------------------------
Contains all of the utility methods for GraphSpace.
Can be considered the controller as it communicates with database.
Located at GraphSpace/graphs/util/db.py

.. automodule:: graphs.util.db
   :members:

Utils - db_conn.py
--------------------------------------
Contains the connection between DJango and the database for GraphSpace.
Located at GraphSpace/graphs/util/db_conn.py

.. automodule:: graphs.util.db_conn
   :members:

Utils - db_init.py
---------------------------------------
Contains table references to SQLite. Located at GraphSpace/graphs/util/db_init.py

Utils - json_converter.py
---------------------------------------
Converts graphs from CytoscapeWeb to CytoscapeJS. Located at GraphSpace/graphs/util/json_converter.py

.. automodule:: graphs.util.json_converter
	:members:

Utils - paginator.py
---------------------------------------
Paginates all graphs that are retrieved. Located at GraphSpace/graphs/util/paginator.py

.. automodule:: graphs.util.paginator
	:members:

