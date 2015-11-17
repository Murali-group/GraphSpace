import sys
import bcrypt
import json
import random
import string
import uuid

from collections import Counter, defaultdict
from operator import itemgetter
from itertools import groupby
from datetime import datetime
from django.core.mail import send_mail
import sqlite3 as lite

from django.conf import settings

from json_validator import validate_json, assign_edge_ids, convert_json
import sqlalchemy, sqlalchemy.orm
from graphs.util.db_conn import Database
import graphs.util.db_init as db_init
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_, or_, tuple_
from sqlalchemy import distinct

import graphs.models as models

data_connection = db_init.db

# Name of the database that is being used as the backend storage
DB_NAME = settings.DB_FULL_PATH
URL_PATH = settings.URL_PATH

def add_everyone_to_password_reset():
	'''
		Adds all users to password reset table (cold-start).
		Only use this once so we know crypto algorithm used 
		for forgot password functionalities

	'''

	#create a new db session
	db_session = data_connection.new_session()
	
	try:
		# Get all users that are currently in the user table
		user_ids = db_session.query(models.User.user_id).all()
		
		# Go through each username and add it to the password_reset table
		for user_id in user_ids:
			# This is done to remove the unicode encoding and simply 
			# extract the string
			user_id  = user_id[0]
			add_user_to_password_reset(user_id, db_session = db_session)

	except NoResultFound:
		print "There are no users in the database"
		return None
	
	db_session.close()

def add_user_to_password_reset(email, db_session=None):
	'''
		Adds a specific user to password_reset table.
		If email is in this, it automatically sends email to change 
		password for that account the next time the user logs on

		:param email: Email of the user for GraphSpace
		:param db_session: database connection (See sqlalchemy.org for more information)
	'''
	# Get database connection
	db_session = db_session or data_connection.new_session()

	# Get the user if they exist
	user_id = db_session.query(models.User.user_id).filter(models.User.user_id == email).first()
	
	# Generate unique code that GraphSpace will use to identify
	# which user is trying to reset their password
	code = id_generator()

	# Create new entry to be inserted into password_reset table
	reset_user = models.PasswordReset(id = None, user_id = email, code = code, created = datetime.now())
	
	# Commit the changes to the database
	db_session.add(reset_user)
	db_session.commit()

def emailExists(email):
	'''
		Checks to see if a user's email exists.

		:param email: Email of user
		:return boolean: True if user exists, false otherwise
	'''
	#create a new db session
	db_session = data_connection.new_session()

	try:
		# Get the user if they exist
		user = db_session.query(models.User).filter(models.User.user_id == email).one()
		# Get the string representation from the tuple
		db_session.close()
		return user
	except NoResultFound:
		db_session.close()
		return None

def need_to_reset_password(email):
	'''
		Checks to see if a user needs to reset their password.
		If email is in password_reset email, they do, otherwise, not.

		:param email: Email of the user in GraphSpace
	'''
	#create a new db session
	db_session = data_connection.new_session()

	try:
		# If email exists in password_reset table, then the user has to reset their password
		user_id = db_session.query(models.PasswordReset.user_id).filter(models.PasswordReset.user_id == email).one()
		return True
	except NoResultFound:
		print "User: " + email + " not found!"
		return None

	db_session.close()

def sendForgotEmail(email):
	'''
		Emails the user to reset their password.

		:param email of user
	'''

	#create a new db session
	db_session = data_connection.new_session()

	try:
		# Retrieve reset code attached to email
		reset_code = db_session.query(models.PasswordReset.code).filter(models.PasswordReset.user_id == email).one()

		# Construct email message
		mail_title = 'Password Reset Information for GraphSpace!'
		message = 'Please go to the following url to reset your password: ' + URL_PATH + 'reset/?id=' + reset_code[0]
		emailFrom = "GraphSpace Admin"
		
		# Sends email to respective user
		send_mail(mail_title, message, emailFrom, [email], fail_silently=True)
		db_session.close()
		return "Email Sent!"
	except NoResultFound:
		print "User " + email + " does not exist"
		db_session.close()
		return None

def retrieveResetInfo(reset_code):
	'''
		Retrieves the reset information for a user (for comparing which user it is).

		:param reset_code: Code that the user has to match to HTTP GET request
		:return account: Account associated with the code 
	'''

	#create a new db session
	db_session = data_connection.new_session()

	try:
		# Obtain email attached to code -> code that was send to email address
		# This is a verification step to ensure code is legit
		user_id_to_reset = db_session.query(models.PasswordReset.user_id).filter(models.PasswordReset.code == reset_code).one()
		# Retrieve string from unicode
		user_id_to_reset = user_id_to_reset[0]
		db_session.close()
		return user_id_to_reset
	except NoResultFound:
		print "Code provided is not correct"
		db_session.close()
		return None

def resetPassword(username, password):
	'''
		Updates password information about a user.

		:param username: Email of user
		:param password: Password of user

	'''

	#create a new db session
	db_session = data_connection.new_session()

	try:
		# Hash password
		password = bcrypt.hashpw(password, bcrypt.gensalt())
		# Update the password for the user (after encryption of course)
		user_to_reset_pw_for = db_session.query(models.User).filter(models.User.user_id == username).one()
		user_to_reset_pw_for.password = password

		# Remove user's account from password_reset table
		delete_from_password_reset = db_session.query(models.PasswordReset).filter(models.PasswordReset.user_id == username).one()
		db_session.delete(delete_from_password_reset)
		db_session.commit()
		db_session.close()
		return "Password updated successfully"
	except Exception as ex:
		print ex
		print "Password not updated correctly"
		db_session.close()
		return None

#### ONE TIME CODE -- KEEP FOR REFERENCE
def reUploadInconsistentGraphs(data):
	con = None
	try: 
		incosistent_graphs = open("inconsistency.txt", "a")
		con = lite.connect(DB_NAME)
		cur = con.cursor()
		graphs_processed = 1
		for graph in data:

			graph_id = graph[0]
			user_id = graph[1]
			graph_json = json.loads(graph[2])
			created = graph[3]
			modified = graph[4]
			public = graph[5]
			unlisted = graph[6]
			default_layout_id = graph[7]

			print "Processing Graph: ", graph_id, " owned by: ", user_id, "\n", graphs_processed, " processed so far"
			graphs_processed += 1

			if 'data' in graph_json:
				graph_json = json.loads(convert_json(graph[2]))

			node_list = []

			for node in graph_json['graph']['nodes']:
				node_list.append(str(node['data']['id']))

			cur.execute('select node_id from node where graph_id=? and user_id =?', (graph_id, user_id))

			nodes = cur.fetchall()

			mark_for_deletion = False

			if len(nodes) != len(node_list):
				print "Nodes don't match"
				mark_for_deletion = True

			unspecified_nodes = ""

			for node in nodes:
				node = str(node[0])
				if node not in node_list:
					print "Unspecified node: ", node
					unspecified_nodes += node + ", "
					mark_for_deletion = True
				
			if mark_for_deletion == True:
				incosistent_graphs.write(graph_id + '\t' + user_id + "\t" + created + "\t" + modified + "\t" + unspecified_nodes + "\n" )
				cur.execute('delete from graph where graph_id = ? and user_id = ?', (graph_id, user_id))
				cur.execute('delete from node where graph_id = ? and user_id = ?', (graph_id, user_id))
				cur.execute('delete from edge where graph_id = ? and user_id = ?', (graph_id, user_id))
				cur.execute('delete from graph_to_tag where graph_id=? and  user_id=?', (graph_id, user_id))
				con.commit()
				result = insert_graph(user_id, graph_id, graph[2], created=created, modified=modified, public=public, unlisted=unlisted, default_layout_id=default_layout_id, skip=True)
				if result != None:
					print result
				else:
					print "Reinserted: " + graph_id

		print "Done processing"
		incosistent_graphs.close()
	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def checkPublicNodeEdgeConsistency():
	'''
		Goes through public graph JSONs in GraphSpace database and makes sure 
		that the node and edge table have the appropriate 
		values and nothing that shouldn't be there.

	'''
	con = None
	try: 
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select * from graph')
		data = cur.fetchall()

		if data == None:
			return

		reUploadInconsistentGraphs(data)

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def checkNodeEdgeConsistencyOfUser(user_id):
	'''
		Goes through JSONs in GraphSpace database and makes sure 
		that the node and edge table have the appropriate 
		values and nothing that shouldn't be there.

	'''
	con = None
	try: 
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select * from graph where user_id=?', (user_id, ))

		data = cur.fetchall()
		reUploadInconsistentGraphs(data)

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()


	# END CONVERSIONS

def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
	'''
		Generates an unique alphanumeric ID of specific size.

		:param size: Size of random string
		:param chars: Subset of characters to generate random string of
		:return string: Random string that adhere to the parameter properties
	'''
	return ''.join(random.choice(chars) for _ in range(size))

def get_valid_user(username, password):
	'''
		Checks to see if a user/password combination exists.
		
		:param username: Email of the user in GraphSpace
		:param password: Password of the user
		:return username: <Username> | None if wrong information
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get user if they exist in the database
		valid_user = db_session.query(models.User).filter(models.User.user_id == username).one()
		# If hashed password != the hashed password in the database, user trying to log in is not a valid user of GraphSpace
		if bcrypt.hashpw(password, valid_user.password) != valid_user.password:
			db_session.close()
			return None

		db_session.close()
		return valid_user
	except NoResultFound:
		db_session.close()
		return None	

def get_graph(user_id, graph_id):
	'''
		Gets the graph.

		@param user_id: Owner of graph
		@param graph_id: ID of graph
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Gets graph 
		graph = db_session.query(models.Graph).filter(models.Graph.user_id == user_id).filter(models.Graph.graph_id == graph_id).one()
		db_session.close()
		return graph
	except NoResultFound:
		db_session.close()
		return None

def graph_exists(user_id, graph_id):
	'''
		Checks to if graph exists.

		@param user_id: Owner of graph
		@param graph_id: ID of graph
	'''
	graph = get_graph(user_id, graph_id)

	if graph == None:
		return False
	else:
		return True

def get_default_layout(uid, gid):
	'''
		Gets the default layout for a graph.
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Retrieve the specific graph
		graph_being_searched = get_graph(uid, gid)

		# Retrieve the saved layout from the database
		default_layout = db_session.query(models.Layout).filter(models.Layout.layout_id == graph_being_searched.default_layout_id).one()
		db_session.close()

		# Convert JSON to cytoscape recognized format
		return json.dumps({"json": cytoscapePresetLayout(json.loads(default_layout.json))})
	except NoResultFound:
		db_session.close()
		return json.dumps(None)	

def get_default_layout_id(uid, gid):
	'''
		Gets the default layout for a graph.
	'''
	# Get the graph
	graph = get_graph(uid, gid)

	if graph != None:
		return graph.default_layout_id
	else:
		return None

def get_layout(layout_id):
	'''
		Gets the layout of ID.

		@param layout_id: Id of layout
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Gets the layout for that specific ID
		layout = db_session.query(models.Layout).filter(models.Layout.layout_id == layout_id).one()
		db_session.close()
		return layout
	except NoResultFound:
		db_session.close()
		return None	

def get_default_layout_name(uid, gid):
	'''
		Gets the default layout for a graph.
	'''
	# Get the specific graph
	graph = get_graph(uid, gid)

	# If the graph exists and has a default layout id
	if graph != None and graph.default_layout_id != None:

		# Get the layout from the database
		default_layout = get_layout(graph.default_layout_id)

		# If the layout exists, return its name
		if default_layout != None:
			return default_layout.layout_name
	else:
		return None

def set_layout_context(request, context, uid, gid):
	'''
		Sets the entire context of a graph to be viewed.  This is needed for sending information to the front-end

		:param request: HTTP Request of graph to view
		:param context: Dictionary containing all the variables to send to the front-end
		:param uid: The owner of the graph
		:param gid: Graph name to view
		:return context: Filled in dictionary with all variables to send to the front-end
	'''
	layout_to_view = None

    # if there is a layout specified in the request (query term), then render that layout
	if len(request.GET.get('layout', '')) > 0:

		# If the layout is not one of the automatic layout algorithms
		if request.GET.get('layout') != 'default_breadthfirst' and request.GET.get('layout') != 'default_concentric' and request.GET.get('layout') != 'default_dagre' and request.GET.get('layout') != 'default_circle' and request.GET.get('layout') != 'default_cose' and request.GET.get('layout') != 'default_cola' and request.GET.get('layout') != 'default_arbor' and request.GET.get('layout') != 'default_springy':
		    
		    # Check to see if the user is logged in
		    temp_uid = None
		    if 'uid' in context:
		    	temp_uid = context['uid']

	    	# Based on the logged in user and the graph, check to see if 
	    	# there exists a layout that matches the query term
		    graph_json = get_layout_for_graph(request.GET.get('layout'), gid, uid, temp_uid)
		    
		    # If the layout either does not exist or the user is not allowed to see it, prompt them with an erro
		    if graph_json == None:
		    	context['Error'] = "Layout: " + request.GET.get('layout') + " either does not exist or " + uid + " has not shared this layout yet.  Click <a href='" + URL_PATH + "graphs/" + uid + "/" + gid + "'>here</a> to view this graph without the specified layout."
		    
	    	# Return layout JSON
		    layout_to_view = json.dumps({"json": graph_json})

		    # Still set the default layout for the graph, if it exists
		    context['default_layout'] = get_default_layout_id(uid, gid)
		else:

			# If there is a layout that is an automatic algorithm, simply
			# return the default layout because the front-end JavaScript library
			# handles the movement clientside
			layout_to_view = get_default_layout(uid, gid)
			context['default_layout'] = layout_to_view

		# Set layout name to add to the query term 
		context['layout_name'] = request.GET.get('layout')
	else:
		# If there is no layout specified, simply return the default layout
		# if it exists
		layout_to_view = get_default_layout(uid, gid)
		context['default_layout'] = get_default_layout_id(uid, gid)
		context['layout_name'] = get_default_layout_name(uid, gid)
		
	context['default_layout_name'] = get_default_layout_name(uid, gid)
	# send layout information to the front-end

	# Pass information to the template
	context['layout_to_view'] = layout_to_view
	context['layout_urls'] = URL_PATH + "graphs/" + uid + "/" + gid + "?layout="

	search_type = None

	# Get the search term to highlight once we load the layout for the graph
	if 'partial_search' in request.GET:
	    search_type = 'partial_search'
	elif 'full_search' in request.GET:
	    search_type = 'full_search'

    # If user is logged in, display my layouts and shared layouts
	if 'uid' in context:
		context['my_layouts'] = get_my_layouts_for_graph(uid, gid, context['uid'])
		context['shared_layouts'] = list(set(get_shared_layouts_for_graph(uid, gid, context['uid']) + get_public_layouts_for_graph(uid, gid) + get_my_shared_layouts_for_graph(uid, gid, context['uid'])))
		context['my_shared_layouts'] = get_my_shared_layouts_for_graph(uid, gid, context['uid'])
	else:
		# Otherwise only display public layouts
		context['my_layouts'] = []
		context['shared_layouts'] = get_public_layouts_for_graph(uid, gid)

	return context

def retrieve_cytoscape_json(graphjson):
	'''
		Converts JSON to CytoscapeJS standards

		:param graphjson: JSON of graph to render on CytoscapeJS
		:return JSON: CytoscapeJS-compatible graphname
	'''

	temp_json = json.loads(graphjson)['graph']

    # for Cytoscape.js, if data is in properties, then we need to convert (main difference)
	if 'data' in temp_json:
	    return convert_json(graphjson)
	else:
	    return graphjson

def get_base_urls(view_type):
	'''
		Assigns urls to the blue buttons viewed at the graphs/ page

		:param view_type: Type of view (shared, public etc)
		:return URL: Link to the specified view_type
	'''

	# Modify the url of the buttons depending on the page that the user is on
	if view_type == 'shared':
	    return URL_PATH + "graphs/shared/"
	elif view_type == 'public':
	    return URL_PATH + "graphs/public/"
	elif view_type == 'all':
	    return URL_PATH + "graphs/all/"
	else:
	    return URL_PATH + "graphs/"

def get_all_info_for_graph(uid, gid):
	'''
		Returns JSON, public, and graph id of the graph

		@param uid: Owner of graph
		@param graph_id: ID of graph
	'''
	# Get the graph
	graph = get_graph(uid, gid)

	if graph == None:
		return None

	return (graph.json, graph.public, graph.graph_id)

def get_graphs_for_view_type(context, view_type, uid, request):
	'''
		Gets the graphs that are associated with a certain view from the user
		
		:param context: Dictionary containing values to pass to front-end
		:param view_type: Type of view to render (my graphs, shared, public)
		:param uid: Owner of the graph
		:param request: Get request
		:return context: Dictionary containing values to pass to front-end
	'''

	# Lists to hold all tag terms and search terms that are beign queried
	tag_list = []
	search_list = []

	# Keep track of type of search that user specified
	search_type = None

	# Partial search may be thought of as "contains" matching
    # Exact search may be though of as "identical" matching
	if 'partial_search' in request.GET:
		search_type = 'partial_search'
	elif 'full_search' in request.GET:
		search_type = 'full_search'

	# Get search terms from query
	search_terms = request.GET.get(search_type)

	# Get tag terms from query
	tag_terms = request.GET.get('tags') or request.GET.get('tag')

	# Get ordered terms for query (ordered being if they want to sort table by its columns)
	order_by = request.GET.get('order')
	
	# Extract tags from query
	if tag_terms and len(tag_terms) > 0:
		cleaned_tags = tag_terms.split(',')
		client_side_tags = ""
		# Goes through each tag, making it a string
		# so the url will contain those tags as a part
		# of the query string
		for tags in xrange(len(cleaned_tags)):
		    cleaned_tags[tags] = cleaned_tags[tags].strip()
		    # If user enters in a blank tag, delete it
		    if len(cleaned_tags[tags]) == 0:
		    	del cleaned_tags[tags]
	    	# Multiple tags are distinguished by commas, so we add them here
		    client_side_tags = client_side_tags + cleaned_tags[tags] + ','

	    # Remove the last comma since nothing comes after last tag
		client_side_tags = client_side_tags[:len(client_side_tags) - 1]

		# Set tags to the cleaned tags we formulated from the query
		# This is done to append to URL of the different view_types we can have
		# For example: buttons containing My Graphs, Shared, and Public will
		# have query string of tags appended to end of URL
		# This happens in front-end (See graphs/templates/graphs/graphs.html)
		context['tags'] = client_side_tags

		# This is for the side menu, each tag has its own button
		context['tag_terms'] = cleaned_tags

		# Cleaned list of tags ready to be queried in view_graphs method
		tag_list = cleaned_tags

    # Extract search terms from query
	if search_terms and len(search_terms) > 0:
		# Set to true so that front-end will know to apend
		# a search term to all views (My Graphs, Shared, Public)
		context['search_result'] = True

		# Split up search terms by comma
		cleaned_search_terms = search_terms.split(',')

		# Search string to formulate that will contain all search terms
		client_side_search = ""

		# Goes through each search term, making it a string
		# so the url will contain those searches as a part
		# of the query string
		for i in xrange(len(cleaned_search_terms)):
			cleaned_search_terms[i] = cleaned_search_terms[i].strip()
			# Deleted no length search terms
			if len(cleaned_search_terms[i]) == 0:
				del cleaned_search_terms[i]

			# This is for the side menu, each search item has its own button
			client_side_search = client_side_search + cleaned_search_terms[i] + ','

		# Remove last comma
		client_side_search = client_side_search[:len(client_side_search) - 1]

		# All context variables will be recognized in the front end 
		# See (See graphs/templates/graphs/graphs.html)
		context['search_word'] = client_side_search

		# Type of search (partial or exact) -> Used to fill in radio button 
		context['search_type'] = search_type

		# Search terms (Used to append URL to view types: My Graphs, Shared, Public)
		context['search_word_terms'] = cleaned_search_terms

		# Cleaned list of search terms to be queried on
		search_list = cleaned_search_terms

	# If there is no one logged in, display only public graph results
	# my_graphs represents all matching graphs which I own
	# shared_graphs represents all matching graphs which are shared with me
	# public graphs represent all matching graphs available to everyone

	# In order to produce the number of graphs returned that match the query 
	# (for the My Graphs, Shared, and Public buttons), I am also retrieving the len
	# of matched graphs for each view_type.  This feature was requesed by Murali

	# For every query, we need to make request for all the view types (shared, public, my graphs)
	# because we want to notify the user the number of graphs that are available for each view
	# that matches the queries
	if uid == None:
		context['graph_list'] = view_graphs(uid, search_type, search_terms, tag_list, 'public')
		context['my_graphs'] = 0
		context['shared_graphs'] = 0
		if context['graph_list'] == None:
			context['public_graphs'] = 0
		else:
			context['public_graphs'] = len(context['graph_list'])
	else:
		if view_type == 'my graphs':
			context['graph_list'] = view_graphs(uid, search_type, search_list, tag_list, view_type)
			context['my_graphs'] = len(context['graph_list'])
			context['shared_graphs'] = len(view_graphs(uid, search_type, search_list, tag_list, 'shared'))
			context['public_graphs'] = len(view_graphs(uid, search_type, search_list, tag_list, 'public'))
		elif view_type == 'shared':
			context['graph_list'] = view_graphs(uid, search_type, search_list, tag_list, view_type)
			context['my_graphs'] = len(view_graphs(uid, search_type, search_list, tag_list, 'my graphs'))
			context['shared_graphs'] = len(context['graph_list'])
			context['public_graphs'] = len(view_graphs(uid, search_type, search_list, tag_list, 'public'))
		else:
			context['graph_list'] = view_graphs(uid, search_type, search_list, tag_list, view_type)
			context['my_graphs'] = len(view_graphs(uid, search_type, search_list, tag_list, 'my graphs'))
			context['shared_graphs'] = len(view_graphs(uid, search_type, search_list, tag_list, 'shared'))
			context['public_graphs'] = len(context['graph_list'])

	#If user has requested the graphs to be ordered in a certain manner, order them as requested
	if order_by:
		context['graph_list'] = order_information(order_by, search_terms, context['graph_list'])
	else:
		# By default, all graphs are ordered via descending modified date (as per Anna's request)
		context['graph_list'] = order_information("modified_descending", search_terms, context['graph_list'])
	
	return context	

def setDefaultLayout(layoutName, graph_id, graph_owner):
	'''
		Sets default layout of graph.

		@param layoutName: name of layout
		@param graph_id: ID of graph
		@param graph_owner: Owner of graph
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Check to see if graph exists
		graph = db_session.query(models.Graph).filter(models.Graph.user_id == graph_owner).filter(models.Graph.graph_id == graph_id).first()

		if graph == None:
			return "It appears as if the graph requested does not exist."

		# Check to see if the layout is either shared or exists in the database
		layout = db_session.query(models.Layout).filter(models.Layout.graph_id == graph_id).filter(models.Layout.layout_name == layoutName).filter(or_(models.Layout.shared_with_groups == 1, models.Layout.public == 1)).first()

		if layout == None:
			return "You can't set a layout as default layout for graph unless layout is shared and the graph is public!"

		# Update the default layout of the current graph
		graph.default_layout_id = layout.layout_id

		db_session.commit()
		db_session.close()
		return None
	except NoResultFound:
		db_session.close()
		return "Can't set default layout of layout that doesn't exist or you can't access."	

def removeDefaultLayout(layoutName, graph_id, graph_owner):
	'''
		Removes default layout of graph.

		@param layoutName: name of layout
		@param graph_id: ID of graph
		@param graph_owner: Owner of graph
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Get graph being viewed
	graph = db_session.query(models.Graph).filter(models.Graph.graph_id == graph_id).filter(models.Graph.user_id == graph_owner).first()

	if graph == None:
		return "Graph does not exist!"

	# Get the layout to see if it exists
	layout = db_session.query(models.Layout).filter(models.Layout.layout_id == models.Graph.default_layout_id).first()

	if layout == None:
		return "Layout does not exist for this graph!"

	try:
		# If the default layout is deleted, update 
		# graph so that it has no default layout
		if layout.layout_name == layoutName:
			graph.default_layout_id = None
			db_session.commit()
		db_session.close()
		return None
	except Exception as ex:
		print ex
		db_session.close()
		return "An unexpected error occureed: " + ex

def order_information(order_term, search_terms, graphs_list):
	'''
		Orders all graph tuples based on order_term.

		:param order_term Term to order by (example, graph, modified, owner)
		:param search_terms Search terms in query (Needed because all search terms add two column (link to graph and node labels) which offsets references by 2)
		:param graph_list Tuples of graphs
		:return sorted_list Sorted list of graph tuples according to order_term
	'''

	# Each order_term corresponds to sortable columns in the graph tables
	if search_terms:
		if order_term == 'graph_ascending':
			return sorted(graphs_list, key=lambda graph: graph.graph_id)
		elif order_term == 'graph_descending':
			return sorted(graphs_list, key=lambda graph: graph.graph_id, reverse=True)
		elif order_term == 'modified_ascending':
			return sorted(graphs_list, key=lambda graph: graph[4])
		elif order_term == 'modified_descending':
			return sorted(graphs_list, key=lambda graph: graph[4], reverse=True)
		elif order_term == 'owner_ascending':
			return sorted(graphs_list, key=lambda graph: graph.user_id)
		elif order_term == 'owner_descending':
			return sorted(graphs_list, key=lambda graph: graph.user_id, reverse=True)
		else:
			return graphs_list
	else:
		if order_term == 'graph_ascending':
			return sorted(graphs_list, key=lambda graph: graph.graph_id)
		elif order_term == 'graph_descending':
			return sorted(graphs_list, key=lambda graph: graph.graph_id, reverse=True)
		elif order_term == 'modified_ascending':
			return sorted(graphs_list, key=lambda graph: graph.modified)
		elif order_term == 'modified_descending':
			return sorted(graphs_list, key=lambda graph: graph.modified, reverse=True)
		elif order_term == 'owner_ascending':
			return sorted(graphs_list, key=lambda graph: graph.user_id)
		elif order_term == 'owner_descending':
			return sorted(graphs_list, key=lambda graph: graph.user_id, reverse=True)
		else:
			return graphs_list

def view_graphs(uid, search_type, search_terms, tag_terms, view_type):
	'''
		Gets the graphs that are associated with a certain view from the user
		
		:param uid: Owner of the graph
		:param search_type: Type of search (partial or full)
		:param search_terms: Criteria that to filter graphs 
		:param tag_terms: Only display graphs with these tags
		:return context: Dictionary containing values to pass to front-end
	'''

	# If there are graphs that fit search and tag criteria
	if search_terms and tag_terms and len(search_terms) > 0 and len(tag_terms) > 0:
		actual_graphs = []

		# Get all graphs that contain all the search terms
		search_result_graphs = search_result(uid, search_type, search_terms, view_type)
		
		# Get all graphs that contain all the tag terms
		tag_result_graphs = tag_result(uid, tag_terms, view_type)

		tag_graphs = [x[0] for x in tag_result_graphs]
		actual = [x[0] for x in actual_graphs]

		# If it is not already part of final graphs returned, add it in
		for graph in search_result_graphs:
			if graph[0] in tag_graphs and graph[0] not in actual:
				actual_graphs.append(graph)

		return actual_graphs

	# If there are only tag terms
	elif tag_terms and len(tag_terms) > 0:
		return tag_result(uid, tag_terms, view_type)
	# If there are only search terms
	elif search_terms and len(search_terms) > 0:
		return search_result(uid, search_type, search_terms, view_type)
	# Just display the graphs
	else:
		return view_graphs_of_type(view_type, uid)
		
def tag_result(uid, tag_terms, view_type):
	'''
		Gets all graphs that contain the specified tags for a user and a view_type.

		:param uid: Owner of graph
		:param tag_terms: Tags that all graphs must contain
		:param view_type: Type of view to display the graphs in (shared, public)
		:return Graphs: [graphs]
	'''
	if len(tag_terms) > 0:
		# Place holder that stores all the graphs
		initial_graphs_with_tags = []	

		# Create database connection
		db_session = data_connection.new_session()

		# Go through all the tag terms, based on the view type and append them the initial place holder
		for tag in tag_terms:
			intial_graphs_with_tags = []

			if view_type == 'my graphs':
				try:
					intial_graphs_with_tags += db_session.query(models.Graph.graph_id, models.Graph.modified, models.Graph.user_id).filter(models.Graph.graph_id == models.GraphToTag.graph_id).filter(models.Graph.user_id == models.GraphToTag.user_id).filter(models.GraphToTag.tag_id == tag).filter(models.Graph.user_id == uid).all()
				except NoResultFound:
					print 'No graphs that you own match the tag term'

			elif view_type == 'shared':

				# Append all graphs that are shared with groups that the user is a member of
				intial_graphs_with_tags += db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.modified, models.GroupToGraph.user_id).filter(models.GroupToGraph.group_id == models.GroupToUser.group_id).filter(models.GroupToGraph.group_owner == models.GroupToUser.group_owner).filter(models.GroupToUser.user_id == uid).filter(models.GraphToTag.tag_id == tag).filter(models.GraphToTag.graph_id == models.GroupToGraph.graph_id).filter(models.GraphToTag.user_id == models.GroupToGraph.user_id).all()
				# Append all graphs that the user shared for any groups that they own
				intial_graphs_with_tags += db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.modified, models.GroupToGraph.user_id).filter(models.GroupToGraph.group_id == models.Group.group_id).filter(models.Group.owner_id == uid).filter(models.GroupToGraph.group_owner == models.Group.owner_id).filter(models.GraphToTag.tag_id == tag).filter(models.GraphToTag.graph_id == models.GroupToGraph.graph_id).filter(models.GraphToTag.user_id == models.GroupToGraph.user_id).all()
			else:
				try:
					intial_graphs_with_tags += db_session.query(models.Graph.graph_id, models.Graph.modified, models.Graph.user_id).filter(models.Graph.graph_id == models.GraphToTag.graph_id).filter(models.Graph.user_id == models.GraphToTag.user_id).filter(models.GraphToTag.tag_id == tag).filter(models.Graph.public == 1).all()
				except NoResultFound:
					print 'No graphs that you own match the tag term'

		# Go through and count the list of occurrences of matched graph
		graph_repititions = defaultdict(int)

		# Counting the number of occurences
		for graph in intial_graphs_with_tags:
			graph_repititions[graph] += 1

		# Go through and aggregate all graph together
		graph_mappings = defaultdict(list)

		# If the number of times a graph appears matches the number of search terms
		# it is a graph we want (simulating the and operator for all search terms)
		for graph in intial_graphs_with_tags:

			# Graph matches all search terms
			if graph_repititions[graph] == len(tag_terms):

				# If we haven't seen this graph yet 
				if graph not in graph_mappings:
					graph_mappings[graph] = graph
				
		# Go through all the graphs and insert tags for the graphs that match all search terms
		return graph_mappings.values()

	else:
		return []

def search_result(uid, search_type, search_terms, view_type):
	'''
		Returns the graphs that match the search terms and the view type.

		:param uid: Owner of the graph
		:param search_type: Type of search to perform (partial or full)
		:param search_terms: Terms to search for
		:param view_type: Type of view to render the graphs for
		:return Graphs: [graphs]
	'''

	# If it is a search type that is not recognized, return empty list
	if search_type != 'partial_search' and search_type !=  'full_search':
		return []

	# Make into list if it is not a lsit
	if not isinstance(search_terms, list):
		search_terms = search_terms.split(',')

	# If there are any search terms
	if len(search_terms) > 0:

		# List to keep track of all matched graphs
		initial_graphs_from_search = []

		# Get connection to database
		data_session = data_connection.new_session()

		# Go through each search term, aggregating 
		# all graphs that match the specific search term
		for search_word in search_terms:
			# matched_graphs contains a list of all graphs that match the specific search term
			matched_graphs = []
			# First, we check to see if there are any graphs that have a graph name that matches the search term
			matched_graphs += find_all_graphs_containing_search_word(uid, search_type, search_word, view_type, data_session)

			# ":" indicates that search_word may be an edge
			if ':' in search_word:
				# append all graphs that contain an edge which matches the search_word
				matched_graphs += find_all_graphs_containing_edges(uid, search_type, search_word, view_type, data_session)
			# otherwise append all graphs that contain a node which matches the search word
			else:
				matched_graphs += find_all_graphs_containing_nodes(uid, search_type, search_word, view_type, data_session)

			# Go through all matched graphs
			# If there is a graph that appears multiple times in the list
			# combine their result.
			# Effectively, a graph may appear at most one time for each search word
			matched_graphs = combine_similar_graphs(matched_graphs)

			# Add condensed tuples to list of graphs matched
			initial_graphs_from_search += matched_graphs 

		# Go through and count the list of occurrences of matched graph
		graph_repititions = defaultdict(int)

		# Counting the number of occurences
		for graph_tuple in initial_graphs_from_search:
			key = graph_tuple[0] + graph_tuple[4]
			graph_repititions[key] += 1

		# Go through and aggregate all graph together
		graph_mappings = defaultdict(list)

		# If the number of times a graph appears matches the number of search terms
		# it is a graph we want (simulating the and operator for all search terms)
		for graph_tuple in initial_graphs_from_search:
			key = graph_tuple[0] + graph_tuple[4]

			graph_tuple = list(graph_tuple)

			# Placeholder for tags of the graph
			graph_tuple.insert(1, "")

			# Graph matches all search terms
			if graph_repititions[key] == len(search_terms):

				# If we haven't seen this graph yet 
				if key not in graph_mappings:
					graph_mappings[key] = tuple(graph_tuple)
				else:
					# Combine result of previous tuple
					old_tuple = list(graph_mappings[key])

					# If there is already a matching node/edge id
					if len(old_tuple[2]) > 0 and len(graph_tuple[2]) > 0:
						old_tuple[2] += ", " + graph_tuple[2]
						old_tuple[3] += ", " + graph_tuple[3]
					# Otherwise, simply insert this graph tuples id
					else:
						old_tuple[2] += graph_tuple[2]
						old_tuple[3] += graph_tuple[3]

					graph_mappings[key] = tuple(old_tuple)

		# Go through all the graphs and insert tags for the graphs that match all search terms
		return graph_mappings.values()
	else:
		return []

def combine_similar_graphs(matched_graphs):
	'''
		Go through list of all matched graphs and combine results if graph appears multiple times.

		@param matched_graphs: List of graphs, nodes, edges that all have reference to graph id via respective models (SQLAlchemy)
	'''
	graph_entry = dict()

	# Go through all the matching graphs/nodes/edges depending on the type of match
	for graph in matched_graphs:
		# If graph contains a matching node
		if hasattr(graph, 'node_id'):
			key = graph.graph_id + graph.user_id
			# If graph has not been encountered yet, insert new tuple
			if key not in graph_entry:
				# Construct new entry
				new_graph_entry = (graph.graph_id, graph.node_id + "(" + graph.label + ")", graph.label, graph.modified, graph.user_id)

				# Add to dict
				graph_entry[key] = new_graph_entry
			else:
				# If graph has been discovered, append node id details to graph tuple
				cur_graph_entry = list(graph_entry[key])
				if len(cur_graph_entry[1]) == 0:
					cur_graph_entry[1] += graph.node_id + "(" + graph.label + ")"
					cur_graph_entry[2] += graph.label
				else:
					cur_graph_entry[1] += ", " + graph.node_id + "(" + graph.label + ")"
					cur_graph_entry[2] += ", " + graph.label

				# Add modified entry
				graph_entry[key] = tuple(cur_graph_entry)

		# If graph contains a matching edge
		elif hasattr(graph, 'head_node_id'):
			key = graph.graph_id + graph.user_id

			# If graph has been encountered yet, insert new tuple
			if key not in graph_entry:
				graph_info = get_graph(graph.user_id, graph.graph_id)

				# Construct new entry
				new_graph_entry = (graph.graph_id, graph.edge_id + "(" + graph.head_node_id + "-" + graph.tail_node_id + ")", graph.edge_id, graph_info.modified, graph_info.user_id, graph_info.public)

				# Add to dict
				graph_entry[key] = new_graph_entry
			else:
				# If graph already has been encountered
				cur_graph_entry = list(graph_entry[key])
				if len(cur_graph_entry[1]) == 0:
					cur_graph_entry[1] += graph.edge_id + "(" + graph.head_node_id + "-" + graph.tail_node_id + ")"
					cur_graph_entry[2] += graph.edge_id
				else:
					cur_graph_entry[1] += ", " + graph.edge_id + "(" + graph.head_node_id + "-" + graph.tail_node_id + ")"
					cur_graph_entry[2] += ", " + graph.edge_id

				# Add appended entry
				graph_entry[key] = tuple(cur_graph_entry)

		# If graph contains a term that is in the id of the graph
		else: 
			key = graph.graph_id + graph.user_id
			# If graph has not yet been encountered, append tuple to list of graphs encountered
			if key not in graph_entry:
				# Create new entry
				new_graph_entry = (graph.graph_id, "", "", graph.modified, graph.user_id)

				# Add new entry to dict
				graph_entry[key] = new_graph_entry

	return graph_entry.values()

def find_all_graphs_containing_search_word(uid, search_type, search_word, view_type, db_session):
	'''	
		Finds graphs that have the matching graph name.

		:param uid: Owner of the graph
		:param search_type: Type of search (full_search or partial_search)
		:param search_word: Graph names being searched for
		:param view_type: Type of view to limit the graphs to (my graphs, shared, public)
		:param cur: Database cursor
		:return Graphs: [Graphs]
	'''
	matched_graphs = []
	# Return all graphs that have a graph name that partially matches the search word
	if search_type == 'partial_search':
		# Select graphs that match the given view type
		if view_type == "my graphs":
			matched_graphs = db_session.query(models.Graph.graph_id, models.Graph.user_id, models.Graph.modified).filter(models.Graph.graph_id.like("%" + search_word + "%")).filter(models.Graph.user_id == uid).all()
		elif view_type == "shared":
			matched_graphs = db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id, models.GroupToGraph.modified).filter(models.GroupToGraph.group_id == models.GroupToUser.group_id).filter(models.GroupToGraph.group_owner == models.GroupToUser.group_owner).filter(models.GroupToUser.user_id == uid).filter(models.GroupToGraph.graph_id.like("%" + search_word + "%")).all()
			matched_graphs += db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id, models.GroupToGraph.modified).filter(models.GroupToGraph.graph_id.like("%" + search_word + "%")).filter(models.Group.owner_id == uid).filter(models.Group.group_id == models.GroupToGraph.group_id).filter(models.Group.owner_id == models.GroupToGraph.group_owner).all()
		elif view_type == "public":
			matched_graphs = db_session.query(models.Graph.graph_id, models.Graph.user_id, models.Graph.modified, models.Graph.public).filter(models.Graph.graph_id.like("%" + search_word + "%")).filter(models.Graph.public == 1).all()

	# Return all graphs that have a gaph name that exactly matches the search word
	elif search_type == 'full_search':
		# Select graphs that match the given view type
		if view_type == "my graphs":
			matched_graphs = db_session.query(models.Graph.graph_id, models.Graph.modified, models.Graph.user_id, models.Graph.public).filter(models.Graph.graph_id == search_word).filter(models.Graph.user_id == uid).all()
		elif view_type == "shared":
			matched_graphs = db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id, models.GroupToGraph.modified).filter(models.GroupToGraph.group_id == models.GroupToUser.group_id).filter(models.GroupToGraph.group_owner == models.GroupToUser.group_owner).filter(models.GroupToUser.user_id == uid).filter(models.GroupToGraph.graph_id == search_word).all()
			matched_graphs += db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id, models.GroupToGraph.modified).filter(models.GroupToGraph.graph_id == search_word).filter(models.Group.owner_id == uid).filter(models.Group.group_id == models.GroupToGraph.group_id).filter(models.Group.owner_id == models.GroupToGraph.group_owner).all()
		elif view_type == "public":
			matched_graphs = db_session.query(models.Graph.graph_id, models.Graph.modified, models.Graph.user_id, models.Graph.public).filter(models.Graph.graph_id == search_word).filter(models.Graph.public == 1).all()

	graph_dict = dict()

	# Remove duplicates for all graphs that match have the same graph matching search term
	for graph in matched_graphs:
		key = graph.graph_id + graph.user_id
		if key in graph_dict:
			continue
		else:
			graph_dict[key] = graph

	return graph_dict.values()

def find_all_graphs_containing_edges(uid, search_type, search_word, view_type, db_session):
	'''
		Finds graphs that have the edges that are being searched for.

		:param uid: Owner of the graph
		:param search_type: Type of search (partial_search or full_search)
		:param search_word: Edge being searched for
		:param view_type: Type of view to limit the graphs to
		:param cur: Database cursor
		:return Edges: [Edges]
	'''

	# List to keep track of all graphs that contain edges that match the search_word
	initial_graphs_matching_edges = []

	# Separate the edge into its two node ID's
	# This is done because in the database, an edge ID is comprised of target:source nodes
	node_ids = search_word.split(":")

	# Get head and tail node references
	head_node = node_ids[0]
	tail_node = node_ids[1]

	# List of all head node ids
	head_nodes = []

	# List of all tail node ids
	tail_nodes = []

	# Match all edges that contain the edges that exactly match the search_word
	if search_type == "full_search":

		# Get all (head) nodes that contain a label matching search_word
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.label == head_node).all()
		
		# Get all (tail) nodes that contain a label matching search_word
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.label == tail_node).all()

		# Get all (head) nodes that contain a node id matching search_word 
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id == head_node).all()

		# Get all (tail) nodes that contain a node id matched search_word 
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id == tail_node).all()
		
	elif search_type == "partial_search":

		# Get all (head) nodes that contain a partially matching label
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.label.like("%" + head_node + "%")).all()
		
		# Get all (tail) nodes that contain a label partially matching label
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.label.like("%" + tail_node + "%")).all()

		# Get all (head) nodes that contain a node id partially matching search_word 
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id.like("%" + head_node + "%")).all()
		
		# Get all (head) nodes that contain a node id partially matching search_word 
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id.like("%" + tail_node + "%")).all()

	# Remove all the duplicates
	head_nodes = list(set(head_nodes))
	tail_nodes = list(set(tail_nodes))

	# Go through head and tail nodes to see if there are any graphs
	# that match the given view type (my graphs, shared, public).
	# In other words, return all graphs that having matching edges
	# for the given view type.

	# TODO: ASK MURALI ABOUT BIDIRECTION EDGES

	# If there are both head and tail nodes
	if len(head_nodes) > 0 and len(tail_nodes) > 0:
		# Go through all permutations of these nodes
		# compile graphs that match the given view_type (my graphs, shared, public)
		for i in xrange(len(head_nodes)):
			for j in xrange(len(tail_nodes)):
				h_node =  head_nodes[i][0]
				t_node =  tail_nodes[j][0]
				# For each view type, we query edges twice because we use head:tail and tail:head (to resolve undirected edge search issue)
				if view_type == "public":
					initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.Edge.head_node_id == h_node).filter(models.Edge.tail_node_id == t_node).filter(models.Edge.graph_id == models.Graph.graph_id).filter(models.Graph.public == 1).all()
					initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.Edge.head_node_id == t_node).filter(models.Edge.tail_node_id == h_node).filter(models.Edge.graph_id == models.Graph.graph_id).filter(models.Graph.public == 1).all()
				elif view_type == "shared":
					initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.GroupToGraph.user_id == uid).filter(models.Edge.graph_id == models.GroupToGraph.graph_id).filter(models.Edge.head_node_id == t_node).filter(models.Edge.tail_node_id == h_node).filter(models.Edge.graph_id == models.Graph.graph_id).all()
					initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.GroupToGraph.user_id == uid).filter(models.Edge.graph_id == models.GroupToGraph.graph_id).filter(models.Edge.head_node_id == t_node).filter(models.Edge.tail_node_id == h_node).filter(models.Edge.graph_id == models.Graph.graph_id).all()
				else:
					initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.Edge.head_node_id == h_node).filter(models.Edge.tail_node_id == t_node).filter(models.Edge.graph_id == models.Graph.graph_id).filter(models.Edge.user_id == uid).all()
					initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.Edge.head_node_id == t_node).filter(models.Edge.tail_node_id == h_node).filter(models.Edge.graph_id == models.Graph.graph_id).filter(models.Edge.user_id == uid).all()


		graph_dict = dict()

		# Remove duplicates for all graphs that match have the same edge matching search term
		for edge in initial_graphs_matching_edges:
			key = edge.head_node_id + edge.graph_id + edge.user_id + edge.tail_node_id + edge.edge_id
			if key in graph_dict:
				continue
			else:
				graph_dict[key] = edge

		return graph_dict.values()
	else:
		return []

def find_all_graphs_containing_nodes(uid, search_type, search_word, view_type, db_session):
	'''
		Finds graphs that have the nodes that are being searched for.

		:param uid: Owner of the graph
		:param search_type: Type of search (partial_search or full_search)
		:param search_word: Node being searched for
		:param view_type: Type of view to limit the graphs to
		:param db_session: Database session
		:return Nodes: [Nodes]
	'''

	# Graphs that contained nodes matching the search_word
	initial_graphs_matching_nodes = []

	# If search type wants to partially match node
	if view_type == "my graphs":

		if search_type == "partial_search":
			# Get all partially matching nodes containing the label
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.label.like("%" + search_word + "%")).filter(models.Node.user_id == uid).all()
			
			# Get all partially matching nodes containing the node id
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.node_id.like("%" + search_word + "%")).filter(models.Node.user_id == uid).all()
		else:
			# Get all partially matching nodes containing the label
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.label == search_word).filter(models.Node.user_id == uid).all()
			
			# Get all partially matching nodes containing the node id
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.node_id == search_word).filter(models.Node.user_id == uid).all()
	
	# Shared graphs
	elif view_type == "shared":
		# Get all the groups that a user is a member of
		groups_user_belongs_to = db_session.query(models.GroupToUser.group_id, models.GroupToUser.group_owner).filter(models.GroupToUser.user_id == uid).all()

		# Get all graphs that are part of groups that the user belongs to
		graphs_in_group = list()

		# Go through each group and add graphs keys to the set
		for single_group in groups_user_belongs_to:
			group_id = single_group.group_id
			group_owner = single_group.group_owner

			graphs_in_group += db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id).filter(models.GroupToGraph.group_id == group_id).filter(models.GroupToGraph.group_owner == group_owner).all()

		# Go through all groups that the user owns
		groups_user_owns = db_session.query(models.Group).filter(models.Group.owner_id == uid).all()

		for single_group in groups_user_owns:
			graphs_in_group += db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id).filter(models.GroupToGraph.group_id == single_group.group_id).filter(models.GroupToGraph.group_owner == single_group.owner_id).all()

		if search_type == "partial_search":
			# Get all graphs that contain a partially matched label and user does not own (since it's shared)
			all_matched_node_graphs = db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.label.like("%" + search_word + "%")).all()

			# Collect all graphs that are shared with user and matches terms
			final_graphs = []

			# Go through all matched graphs to see which graphs 
			# are also shared with user and take the intersection
			for matched in all_matched_node_graphs:
				search_graph = (matched.graph_id, matched.user_id)
				if search_graph in graphs_in_group:
					final_graphs.append(matched)

			# Get all graphs that contain a partially matched node and user does not own (since it's shared)
			all_matched_node_graphs = db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.node_id.like("%" + search_word + "%")).all()

			# Go through all matched graphs to see which graphs 
			# are also shared with user and take the intersection
			for matched in all_matched_node_graphs:
				search_graph = (matched.graph_id, matched.user_id)
				if search_graph in graphs_in_group:
					final_graphs.append(matched)

			initial_graphs_matching_nodes = final_graphs
		else:
			# Get all graphs that contain a partially matched label and user does not own (since it's shared)
			all_matched_node_graphs = db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.label == search_word).all()

			# Collect all graphs that are shared with user and matches terms
			final_graphs = []

			# Go through all matched graphs to see which graphs 
			# are also shared with user and take the intersection
			for matched in all_matched_node_graphs:
				search_graph = (matched.graph_id, matched.user_id)
				if search_graph in graphs_in_group:
					final_graphs.append(matched)

			# Get all graphs that contain a partially matched node and user does not own (since it's shared)
			all_matched_node_graphs = db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.node_id == search_word).all()

			# Go through all matched graphs to see which graphs 
			# are also shared with user and take the intersection
			for matched in all_matched_node_graphs:
				search_graph = (matched.graph_id, matched.user_id)
				if search_graph in graphs_in_group:
					final_graphs.append(matched)

			initial_graphs_matching_nodes = final_graphs
	# public graphs
	else:
		if search_type == "partial_search":
			# Get all partially matching nodes containing the label
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.label.like("%" + search_word + "%")).filter(models.Node.graph_id == models.Graph.graph_id).filter(models.Node.user_id == models.Graph.user_id).filter(models.Graph.public == 1).all()

			# Get all partially matching nodes containing the node id
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.node_id.like("%" + search_word + "%")).filter(models.Node.graph_id == models.Graph.graph_id).filter(models.Node.user_id == models.Graph.user_id).filter(models.Graph.public == 1).all()
		else:
			# Get all partially matching nodes containing the label
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.label == search_word).filter(models.Node.graph_id == models.Graph.graph_id).filter(models.Node.user_id == models.Graph.user_id).filter(models.Graph.public == 1).all()

			# Get all partially matching nodes containing the node id
			initial_graphs_matching_nodes += db_session.query(models.Node.graph_id, models.Node.node_id, models.Node.label, models.Node.modified, models.Node.user_id).filter(models.Node.node_id == search_word).filter(models.Node.graph_id == models.Graph.graph_id).filter(models.Node.user_id == models.Graph.user_id).filter(models.Graph.public == 1).all()

	graph_dict = dict()

	# Remove duplicates for all graphs that match have the same node id and label matching search term
	for graph in initial_graphs_matching_nodes:
		key = graph.graph_id + graph.user_id + graph.label + graph.node_id
		if key in graph_dict:
			continue
		else:
			graph_dict[key] = graph

	return graph_dict.values()

def uploadCyjsFile(username, graphJSON, title):
	'''
		Uploads a .cyjs file as a JSON via /upload.

		@param username: Owner of graph
		@param graphJSON: CYJS of graph
		@param tile: Title of graph
	'''

	try:
		# Create JSON stucture for GraphSpace recognized JSON
		parseJson = {"graph": {"edges": [], "nodes": []}, "metadata": {}}

		# Load JSON from string
		csjs = json.loads(graphJSON)

		# If there is no elements that exist in the provided JSON
		if 'elements' not in csjs:
			return {"Error": "No elements property inside of file!"}

		# If there is no nodes that exist in the provided JSON
		if 'nodes' not in csjs['elements']:
			return {"Error": "File must contain nodes property in elements dictionary!"}

		# If there is no edges that exist in the provided JSON
		if 'edges' not in csjs['elements']:
			return {"Error": "File must contain edges property in elements dictionary!"}

		# Go through nodes and translate properties so CytoscapeJS may render
		for node in csjs['elements']['nodes']:

			# Container for translated node
			tempNode = {"data": {}}

			# Copy over ID
			tempNode['data']['id'] = node['data']['id']

			# Change color property to background color 
			if 'node_fillColor' in node['data'] and len(node['data']['node_fillColor']) > 0:
				# tempNode['data']['background_color'] = rgb_to_hex(node['data']['node_fillColor'])
				tempNode['data']['background_color'] = node['data']['node_fillColor']

			# If user wants to display something in node, add 'content'
			if 'name' in node['data']:
				tempNode['data']['content'] = node['data']['name']

			# No shape is provided as far as I know, so I pad in an ellipse
			tempNode['data']['shape'] = "ellipse"
			parseJson['graph']['nodes'].append(tempNode)

		# Go through all the edges
		for edge in csjs['elements']['edges']:

			tempEdge = {"data": {}}

			# Copy over source and target
			tempEdge['data']['source'] = edge['data']['source']
			tempEdge['data']['target'] = edge['data']['target']

			# If there is a name property, it will be in a popup
			if 'name' in edge['data']:
				tempEdge['data']['popup'] = edge['data']['name']

			# Add edges to json
			parseJson['graph']['edges'].append(tempEdge)

		# If there is a title in the graph
		if 'name' in csjs['data']:
			parseJson['metadata']['name'] = csjs['data']['name']
		else:
			parseJson['metadata']['name'] = "temp_graph"

		# No tags or description since CYJS doesn't give me any
		parseJson['metadata']['tags'] = []
		parseJson['metadata']['description'] = ""

		title = title or parseJson['metadata']['name']

		# Insert converted graph to GraphSpace and provide URL
		# for logged in user
		if username != None:
			result = insert_graph(username, title, json.dumps(parseJson))
			if result == None:
				return {"Success": URL_PATH + "graphs/" + username + "/" + title}
			else:
				return {"Error": result}
		else:
			# Create a unique user and insert graph for that name
			public_user_id = "Public_User_" + str(uuid.uuid4()) + '@temp.com'
			public_user_id = public_user_id.replace('-', '_')
			
			first_request = create_public_user(public_user_id)

			if first_request == None:
				result = insert_graph(public_user_id, title, json.dumps(parseJson))

				if result == None: 
					return {"Success": URL_PATH + "graphs/" + public_user_id + "/" + title}
				else: 
					return {"Error": result}
			else:
				return {"Error": result}
	except Exception as ex:
		return {"Error": "Seems to be an error with " + ex + " property."}
		
def uploadJSONFile(username, graphJSON, title):
	'''
		Uploads JSON file to GraphSpace via /upload.

		@param username: Owner of graph
		@param graphJSON: JSON of graph
		@param title: Title of graph

	'''

	try: 
		# Loads JSON format
		parseJson = json.loads(graphJSON)

		# Creates metadata tag
		if 'metadata' not in parseJson:
			parseJson['metadata'] = {}

		# If name is not provided, name is data
		if 'name' not in parseJson['metadata']:
			parseJson['metadata']['name'] = "graph_" + str(datetime.now())

		title = title or parseJson['metadata']['name']

		# Insert converted graph to GraphSpace and provide URL
		# for logged in user	
		if username != None:
			result = insert_graph(username, title, json.dumps(parseJson))
			if result == None:
				return {"Success": URL_PATH + "graphs/" + username + "/" + title}
			else:
				return {"Error": result}
		else:
			# Create a unique user and insert graph for that name
			public_user_id = "Public_User_" + str(uuid.uuid4()) + '@temp.com'
			public_user_id = public_user_id.replace('-', '_')
			
			first_request = create_public_user(public_user_id)

			if first_request == None:
				result = insert_graph(public_user_id, title, json.dumps(parseJson))
				if result == None: 
					return {"Success": URL_PATH + "graphs/" + public_user_id + "/" + title}
				else: 
					return {"Error": result}
			else:
				return {"Error": result}
	except Exception as ex:
		return {"Error": ex}

def delete_30_day_old_anon_graphs():
	# Create database connection
	db_session = data_connection.new_session()

	# If there are any graphs owned by a public user that are older than 30 days, delete them
	try:
		graph = db_session.query(models.Graph).filter(models.Graph.user_id.like("%Public_User_%")).filter(models.Graph.created >= date('now', '-30 day'))

		db_session.delete(graph)
		db_session.commit()
		db_session.close()
	except NoResultFound:
		db_session.close()

def rgb_to_hex(rgb):
	# Quick wrapper method to 
	# convert rgb values to hex values
	rgbTuple = rgb.split(',')
	rgbNum = []
	for tup in rgbTuple:
		try:
			rgbNum.append(int(tup))
		except ValueError:
			rgbNum.append(tup);


	rgbNum = tuple(rgbNum)
	return '#%02x%02x%02x' % rgbNum

def create_public_user(public_user_id):
	'''
		Creates a public user (temporary)

		@param public_user_id: Id of user
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Create a public user and add to database
		public_user = models.User(user_id = public_user_id, password = "public", admin = 0)
		db_session.add(public_user)
		db_session.commit()
		db_session.close()
		return None
	except NoResultFound:
		db_session.close()


def delete_public_user():
	'''
		Deletes all public users from database.
	'''

	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Delete all public users
		public_users = db_session.query(models.User).filter(models.User.password == "public").all()

		for user in public_user:
			db_session.delete(user)

		db_session.commit()
		db_session.close()

	except NoResultFound:
		db_session.close()
		return None	

def find_edge(uid, gid, edge_to_find, search_type):
	'''
		Finds the id of the edge inside graph
		Used for highlighting elements inside the graph

		:param uid: Owner of graph
		:param gid: Name of graph that is being viewed
		:param edge_to_find: Edge that is being searched for
		:param search_type: Partial or full matching
		:return ID: [ID of edge]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Extract nodes from input
	head_node = edge_to_find.split(':')[0]
	tail_node = edge_to_find.split(':')[1]

	# List containing edges
	edge_list = []

	# Filter by search type
	if search_type == "partial_search":
		# If there is a head and tail node
		if len(head_node) > 0 and len(tail_node) > 0:

			# Find node id's that are being searched for (source and target nodes)
			head_nodes = find_node(uid, gid, head_node, 'partial_search')
			tail_nodes = find_node(uid, gid, tail_node, 'partial_search')

			# Go through all permutations of head and tail node
			# to account for undirected edges
			for i in xrange(len(tail_nodes)):
				for j in xrange(len(head_nodes)):

					try:
						# Aggregate all matching edges (DO THIS TWO TIMES SO ORDER OF HEAD OR TAIL NODE DOESN'T MATTER... THIS IS TO RESOLVE UNDIRECTED EDGE SEARCHING)
						matching_edges = db_session.query(models.Edge).filter(models.Edge.head_node_id == head_nodes[j]).filter(models.Edge.tail_node_id == tail_nodes[i]).filter(models.Edge.user_id == uid).filter(models.Edge.graph_id == gid).all()
						edge_list += matching_edges

						# Aggregate all matching edges (DO THIS TWO TIMES SO ORDER OF HEAD OR TAIL NODE DOESN'T MATTER... THIS IS TO RESOLVE UNDIRECTED EDGE SEARCHING)
						matching_edges = db_session.query(models.Edge).filter(models.Edge.tail_node_id == head_nodes[j]).filter(models.Edge.head_node_id == tail_nodes[i]).filter(models.Edge.user_id == uid).filter(models.Edge.graph_id == gid).all()
						edge_list += matching_edges

					except NoResultFound:
						print "No matching edges"



	else:	
		# Find node id's that are being searched for (source and target nodes)
		head_nodes = find_node(uid, gid, head_node, 'full_search')
		tail_nodes = find_node(uid, gid, tail_node, 'full_search')

		# Go through all permutations of head and tail node
		# to account for undirected edges
		for i in xrange(len(tail_nodes)):
			for j in xrange(len(head_nodes)):

				# If both nodes exist, find label between them
				if tail_node != None and head_node != None:

					try:
						# Aggregate all matching edges (DO THIS TWO TIMES SO ORDER OF HEAD OR TAIL NODE DOESN'T MATTER... THIS IS TO RESOLVE UNDIRECTED EDGE SEARCHING)
						matching_edges = db_session.query(models.Edge).filter(models.Edge.head_node_id == head_node).filter(models.Edge.tail_node_id == tail_node).filter(models.Edge.user_id == uid).filter(models.Edge.graph_id == gid).all()
						edge_list += matching_edges

						# Aggregate all matching edges (DO THIS TWO TIMES SO ORDER OF HEAD OR TAIL NODE DOESN'T MATTER... THIS IS TO RESOLVE UNDIRECTED EDGE SEARCHING)
						matching_edges = db_session.query(models.Edge).filter(models.Edge.tail_node_id == head_node).filter(models.Edge.head_node_id == tail_node).filter(models.Edge.user_id == uid).filter(models.Edge.graph_id == gid).all()
						edge_list += matching_edges

					except NoResultFound:
						print "No matching edges"

	# Get all labels from edges
	edge_labels = []
	for edge in edge_list:
		edge_labels.append(edge.edge_id)

	return edge_labels

def find_node(uid, gid, node_to_find, search_type):
	'''
		Finds the id of the node inside graph
		Used for highlighting elements inside the graph

		:param uid: Owner of graph
		:param gid: Name of graph that is being viewed
		:param search_type: partial or full matching
		:param node_to_find: Node that is being searched for
		:param search_type: Partial or full matching
		:return ID: [ID of node]
	'''

	# Create database connection
	db_session = data_connection.new_session()

	try:
		id_list = []
		# Filter by search types
		if search_type == "partial_search":
			# Get all matching labels
			labels = db_session.query(models.Node.node_id).filter(models.Node.label.like("%" + node_to_find + "%")).filter(models.Node.user_id == uid).filter(models.Node.graph_id == gid).all()

			# Get all matching ids
			node_ids = db_session.query(models.Node.node_id).filter(models.Node.node_id.like("%" + node_to_find + "%")).filter(models.Node.user_id == uid).filter(models.Node.graph_id == gid).all()

			for label in labels:
				if label not in id_list:
					id_list.append(label[0])

			for node_id in node_ids:
				if node_id not in id_list:
					id_list.append(node_id[0])

		else:
			# Get all matching labels
			label = db_session.query(models.Node.node_id).filter(models.Node.label == node_to_find).filter(models.Node.user_id == uid).filter(models.Node.graph_id == gid).first()

			# Get all matching ids
			node_id = db_session.query(models.Node.node_id).filter(models.Node.node_id == node_to_find).filter(models.Node.user_id == uid).filter(models.Node.graph_id == gid).first()

			if label != None and label not in id_list:
				id_list.append(label[0])

			if node_id != None and node_id not in id_list:
				id_list.append(node_id[0])

		db_session.close()
		return id_list
	except NoResultFound:
		db_session.close()
		return []	

def intersect(a, b):
     return list(set(a) & set(b))

def add_unique_to_list(listname, data):
	'''
		Adds all unique items to the specified list
		Also checks to see if the length is > 0 for each item
		inserted into the list

		:param listname: List to put unique elements in
		:param data: Possible duplicate data to search through
		:return listname: [Unique elements]
	'''
	for element in data:
		if element not in listname and len(element) > 0:
			listname.append(element)

	return listname

# -------------------------- REST API -------------------------------

def insert_graph(username, graphname, graph_json, created=None, modified=None, public=0, shared_with_groups=0, default_layout_id=None):
	'''
		Inserts a uniquely named graph under a username.

		:param username: Email of user in GraphSpace
		:param graphname: Name of graph to insert
		:param graph_json: JSON of graph
		:param created: When was graph created
		:param public: Is graph public?
		:param shared_with_groups: Is graph shared with any groups?
		:param default_layout_id: Default layout of the graph
	'''

	# Check to see if graph already exists
	graph_exists = get_graph(username, graphname)

	# If graph already exists for user, alert them
	if graph_exists != None:
		return 'Graph ' + graphname + ' already exists for ' + username + '!'

	# Create database connection
	db_session = data_connection.new_session()

	validationErrors = validate_json(graph_json)

	print validationErrors
	if validationErrors != None:
		return validationErrors 

	# Get the current time
	curTime = datetime.now()

	# Load JSON string into JSON structure
	graphJson = json.loads(graph_json)

	# Needed for old graphs, converts CytoscapeWeb to CytoscapeJS standard
	if 'data' in graphJson['graph']:
		graphJson = json.loads(convert_json(graph_json))

	# Attach ID's to each edge for traversing the element
	graphJson = assign_edge_ids(graphJson)	

	nodes = graphJson['graph']['nodes']
	
	# If we're not passed in any time values, use the current time as timestamps
	if modified == None and created == None:
		modified = curTime
		created = curTime

	# If we're given a creation time but no modified time, use current time
	elif modified == None:
		modified = curTime

	# If we're given a modified time but no creation time, use current time
	elif created == None:
		created = curTime

	# Construct new graph to add to database
	new_graph = models.Graph(graph_id = graphname, user_id = username, json = json.dumps(graphJson, sort_keys=True, indent=4), created = created, modified = modified, public = public, shared_with_groups = shared_with_groups, default_layout_id = default_layout_id)

	db_session.add(new_graph)
	db_session.commit()

	if 'tags' in graphJson['metadata']:
		tags = graphJson['metadata']['tags']
	else:
		tags = []

	# Insert all tags for this graph into tags database
	insert_data_for_graph(graphJson, graphname, username, tags, nodes, curTime, 0, db_session)

	db_session.close()
	# If everything works, return Nothing 
	return None

def insert_data_for_graph(graphJson, graphname, username, tags, nodes, modified, public, db_session):
	'''
		Inserts metadata about a graph into its respective tables.

		:param graphJson: JSON of graph
		:param graphname: Name of graph
		:username: Name of user
		:param: Tags of graph
		:param nodes: Nodes to insert into nodes table
		:param modified: Modification date of tabe
		:param public: Nodes to insert into nodes table
		:param db_session: Database connection
	'''
	# Add all tags for this graph into graph_tag and graph_to_tag tables
	for tag in tags:
		tag_exists = db_session.query(models.GraphTag).filter(models.GraphTag.tag_id == tag).first()

		# If the tag doesn't already exists in the database, add it
		if tag_exists == None:
			new_tag = models.GraphTag(tag_id = tag)
			db_session.add(new_tag)
			db_session.commit()

		# Add to Graph to Tag table so that we can retrieve all graphs with tag
		new_graph_to_tag = models.GraphToTag(graph_id = graphname, user_id = username, tag_id = tag)
		db_session.add(new_graph_to_tag)
		db_session.commit()

	# Go through edges and parse them accordingly
	edges = graphJson['graph']['edges']

	# If there are edges with same source and directed
	dupEdges = []

	# Number to differentiate between two duplicate edges
	rand = 0

	for edge in edges:
		# Is the edge directed?
		is_directed = 1

		# Make edge undirected if it doesn't have target_arrow_shape attribute
		if 'target_arrow_shape' not in edge['data']:
			edge['data']['target_arrow_shape'] = "none"	
			is_directed = 0

		# Keep track of all the duplicate edges
		# If there are two duplicate edges, append a counter and store it as an ID
		if edge['data']['source'] + '-' + edge['data']['target'] in dupEdges:
			rand += 1
			if 'id' not in edge['data']:
				edge['data']['id'] = edge['data']['source'] + '-' + edge['data']['target'] + rand


		# If this is first time we've seen an edge, simply get its ID without the counter
		else:
			if 'id' not in edge['data']:
				edge['data']['id'] = edge['data']['source'] + '-' + edge['data']['target']

		dupEdges.append(edge['data']['source'] + '-' + edge['data']['target'])

		# TRICKY NOTE: An edge's ID is used as the label property
		# The reason is because edge uses an 'id' column as the primary key.
		# The label was the column I decided to avoid completely reconstructing the database
		# POSSIBLE SOLUTION: If edge is bidirectional, we insert two edges with inverse source and target nodes
		if is_directed == 0:
			new_edge = models.Edge(user_id = username, graph_id = graphname, head_node_id = edge['data']['source'], tail_node_id = edge['data']['target'], edge_id = edge['data']['id'], directed = is_directed, id = None)
			db_session.add(new_edge)

			# ASK MURALI ABOUT THIS
			# new_edge = models.Edge(user_id = username, graph_id = graphname, head_node_id = edge['data']['target'], tail_node_id = edge['data']['source'], edge_id = edge['data']['id'], directed = is_directed, id = None)
			# db_session.add(new_edge)

		else:
			new_edge = models.Edge(user_id = username, graph_id = graphname, head_node_id = edge['data']['source'], tail_node_id = edge['data']['target'], edge_id = edge['data']['id'], directed = is_directed, id = None)
			db_session.add(new_edge)

		db_session.commit()

	# Go through all nodes in JSON and add to node table
	for node in nodes:
		# Used for backwards-compatibility since some JSON have label 
		# but new CytoscapeJS uses the content property
		if 'label' in node['data']:
			node['data']['content'] = node['data']['label']
			del node['data']['label']

		# If the node has any content inside of it, display that content, otherwise, just make it an empty string
		if 'content' not in node['data']:
			node['data']['content'] = ""

		# Add node to table
		new_node = models.Node(node_id = node['data']['id'], label = node['data']['content'], user_id = username, graph_id = graphname, modified = modified)

		db_session.add(new_node)
		db_session.commit()
			
def update_graph(username, graphname, graph_json):
	'''
		Updates the JSON for a graph.
	
		:param username: Email of user in GraphSpace
		:param graphname: Name of graph to insert
		:param graph_json: JSON of graph
	'''

	# Get graph
	graph = get_graph(username, graphname)

	# If graph doesn't exist
	if graph == None:
		return "Can't update " + graphname + " because it does not exist for " + username

	# Get database connection
	db_session = data_connection.new_session()

	# Delete from graph
	db_session.delete(graph)
	db_session.commit()

	try:
		# Get all tags for the graph
		gt_to_delete = db_session.query(models.GraphToTag).filter(models.GraphToTag.graph_id == graphname).filter(models.GraphToTag.user_id == username).all()

		# Remove all graph_to_tag associations
		for gt in gt_to_delete:
			db_session.delete(gt)
			db_session.commit()

	except NoResultFound:
		print "No tags for graph"

	try:
		# Delete from edge
		edges_to_delete = db_session.query(models.Edge).filter(models.Edge.graph_id == graphname).filter(models.Edge.user_id == username).all()

		for edge in edges_to_delete:
			db_session.delete(edge)
			db_session.commit()

	except NoResultFound:
		print "No edges in graph to delete"

	try:
		# Delete from node
		nodes_to_delete = db_session.query(models.Node).filter(models.Node.graph_id == graphname).filter(models.Node.user_id == username).all()

		for node in nodes_to_delete:
			db_session.delete(node)
			db_session.commit()

	except NoResultFound:
		print "No nodes in graph to delete"

	# Re-insert graph
	result = insert_graph(username, graphname, graph_json, graph.created, datetime.now(), graph.public, graph.shared_with_groups, graph.default_layout_id)

	return result

def get_graph_json(username, graphname):
	'''
		Get the JSON of the graph to view.

		:param username: Email of user in GraphSpace
		:param password: Password of the user
		:return JSON: JSON of graph to view
	'''
	# Get the graph
	graph = get_graph(username, graphname)

	# If graph doesn't exist, return None
	if graph == None:
		return None

	return graph.json

def delete_graph(username, graphname):
	'''
		Deletes graph from database.

		:param username: Email of user in GraphSpace
		:param password: Password of the user
	'''

	# Get graph
	graph = get_graph(username, graphname)

	if graph == None:
		return

	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Delete graph 
		db_session.delete(graph)

		db_session.commit()
		# Delete from graph_to_tag
		gt = db_session.query(models.GraphToTag).filter(models.GraphToTag.user_id == username).filter(models.GraphToTag.graph_id == graphname).all()

		for g_tags in gt:
			db_session.delete(g_tags)
			db_session.commit()
		# Delete from group_to_graph
		gg = db_session.query(models.GroupToGraph).filter(models.GroupToGraph.user_id == username).filter(models.GroupToGraph.graph_id == graphname).all()

		for g_gruop in gg:
			db_session.delete(g_gruop)
			db_session.commit()
		# Delete from edge
		edge = db_session.query(models.Edge).filter(models.Edge.graph_id == graphname).filter(models.Edge.user_id == username).all()

		for e in edge:
			db_session.delete(e)
			db_session.commit()

		# Delete from node
		node = db_session.query(models.Node).filter(models.Node.user_id == username).filter(models.Node.graph_id == graphname).all()

		for n in node:
			db_session.delete(n)
			db_session.commit()
		# Delete from layout
		layout = db_session.query(models.Layout).filter(models.Layout.graph_id == graphname).filter(models.Layout.user_id == username).all()

		for l in layout:
			db_session.delete(l)
			db_session.commit()
		db_session.commit()
		db_session.close()

	except Exception as ex:
		print ex
		db_session.close()
		return	

def get_all_graphs_for_user(username):
	'''
		Gets all graphs for username

		:param username: Email of user in GraphSpace
		:return Graphs: [graphs]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get all graphs user owns
		user_graphs = db_session.query(models.Graph).filter(models.Graph.user_id == username).all()

		# Get all names of graphs that user owns
		cleaned_user_graph_names = []

		# Get rid of unicode
		for graph in user_graphs:
			cleaned_user_graph_names.append(graph.graph_id)

		db_session.close()
		return cleaned_user_graph_names
	except NoResultFound:
		db_session.close()
		return []

def get_graphs_in_group(group_id, group_owner):
	'''
		Gets graphs in a group.

		@param group_id: Id of group
		@param group_owner: Owner of group
	'''

	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Gets all the graphs in the group
		graphs_in_group = db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.user_id).filter(models.GroupToGraph.group_id == group_id).filter(models.GroupToGraph.group_owner == group_owner).all()
		
		db_session.close()
		return graphs_in_group
	except NoResultFound:
		db_session.close()
		return []	

def get_groups_of_user(user_id):
	'''
		Get all groups that the user owns

		:param user_id: Email of user of GraphSpace
		:return Groups: [group information]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get all groups that user owns
		owned_groups = db_session.query(models.Group).filter(models.Group.owner_id == user_id).all()

		# Get information about graphs in group and format it
		complete_group_information = get_cleaned_group_data(owned_groups, db_session)

		db_session.close()
		return complete_group_information
	except NoResultFound:
		db_session.close()
		return None	

def get_cleaned_group_data(data, db_session):
	'''
		Get all information about group (including number of graphs group has)

		:param data: Information about group
		:param cur: Database cursor
		:return Groups: [gorup information + graphs in group information]
	'''

	# Get information about how many graphs each group contains
	complete_group_information = []

	# For each group that is provided, append the amount of graphs that belong in the group
	# and return it as a tuple

	# Used as the primary method for /groups page
	for group in data:
		cleaned_group = []
		cleaned_group.append(group.name)
		cleaned_group.append(group.description)
		cleaned_group.append(group.owner_id)

		graphs = db_session.query(models.Graph.graph_id).filter(models.GroupToGraph.group_id == group.group_id).filter(models.GroupToGraph.group_owner == group.owner_id).filter(models.GroupToGraph.graph_id == models.Graph.graph_id).filter(models.GroupToGraph.user_id == models.Graph.user_id).all()

		cleaned_group.append(len(graphs))

		# cleaned_group.append(group.public)
		# cleaned_group.append(group.shared_with_groups)
		cleaned_group.append(group.group_id)
		complete_group_information.append(tuple(cleaned_group))

	return complete_group_information

def get_all_groups_with_member(user_id, skip = None):
	'''
		Get all groups that has the user as a member in that group.

		:param user_id: Member to be searched for in all groups
		:return Groups: [Groups that user_id is a member of]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		cleaned_groups = []
		# Get all groups that the user is a member of
		groups_with_member = db_session.query(models.Group).filter(models.Group.group_id == models.GroupToUser.group_id).filter(models.Group.owner_id == models.GroupToUser.group_owner).filter(models.GroupToUser.user_id == user_id).all()

		if skip == None:
			# Format group information
			cleaned_groups = get_cleaned_group_data(groups_with_member, db_session)
		else:
			# Get all groups that the user is a member of
			groups_with_member += db_session.query(models.Group).filter(models.Group.owner_id == user_id).all()
			cleaned_groups = groups_with_member

		db_session.close()
		return cleaned_groups
	except NoResultFound:
		db_session.close()
		return None

def change_description(username, groupId, groupOwner, desc):
	'''
		Changes description of group.

		:param username: person who is requesting the change
		:param groupId: ID of group to change description 
		:param groupOwner: Owner of the group
		:param desc: Description to change to
		:return Error: <error>
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		if username != groupOwner:
			return "You can only change description of group that you own!"

		# Get the group to change the description of
		group = db_session.query(models.Group).filter(models.Group.owner_id == groupOwner).filter(models.Group.group_id == groupId).one()

		group.description = desc

		db_session.commit()
		db_session.close()
		return None
	except Exception as ex:
		db_session.close()
		return ex

def get_group_by_id(groupOwner, groupId):
	'''
		Gets a group information by group id ( REST API option).
		
		:param groupOwner: Owner of the group
		:param groupId: ID of group to be searched for
		:return Group: [Information about group (see REST API in Help section)]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Get the group
	group = db_session.query(models.Group).filter(models.Group.owner_id == groupOwner).filter(models.Group.group_id == groupId).first()

	# If no group is found, return
	if group == None:
		return None

	cleaned_data = []

	# Remove group owner's name from member's list to display in UI
	initial_members = get_group_members(groupOwner, groupId)
	members = []

	# Get all member names
	for member in initial_members:
		if member.user_id != groupOwner:
			members.append(member.user_id)

	# Combine group with members of group
	cleaned_tuple = (group.description, members, group.owner_id, group.name, group.group_id)

	db_session.close()
	return [cleaned_tuple]

def get_group(group_owner, groupId):
	'''
		Gets all information about a certain group (used for groups page exclusively).
        
        :param group_owner: Owner of group to get from server
		:param groupId: ID of groupId
		:return Group: [information of group]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Get the group
	group = db_session.query(models.Group).filter(models.Group.group_id == groupId).filter(models.Group.owner_id == group_owner).first()

	# If no group exists, return
	if group == None:
		db_session.close()
		return None

	cleaned_data = {}

	# Set all properties that are used in the /groups page
	cleaned_data['members'] = get_group_members(group_owner, groupId)
	cleaned_data['owner'] = group.owner_id
	cleaned_data['group_id'] = group.group_id
	cleaned_data['description'] = group.description

	# Get all graph names for group
	graphs = get_graphs_in_group(group.group_id, group.owner_id)

	graph_names = []
	for graph in graphs:
		graph_names.append(graph.graph_id)

	cleaned_data['graphs'] = graphs
	db_session.close()
	return cleaned_data

def get_group_members(groupOwner, groupId):
	'''
		Get all members of a group.

		:param groupOwner: Group Owner 
		:param groupId: Group ID
		:return Members: [Members of group]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get all members of the group
		group_members = db_session.query(models.User).filter(models.User.user_id == models.GroupToUser.user_id).filter(models.GroupToUser.group_owner == groupOwner).filter(models.GroupToUser.group_id == groupId).all()

		# Also get owns of the group as well since owners are technically members of the group too
		# group_members += db_session.query(models.User).filter(models.User.user_id == models.GroupToUser.user_id).filter(models.GroupToUser.group_owner == groupOwner).filter(models.GroupToUser.group_id == groupId).all()

		db_session.close()
		return group_members

	except NoResultFound:
		db_session.close()
		return None

def can_see_shared_graph(logged_in_user, graph_owner, graphname):
	'''
		See if user is allowed to see a graph.

		:param logged_in_user: User that is currently logged in
		:param graph_owner: Owner of graph being viewed
		:param graphname: Name of graph being viewed
		:return boolean: True if can see it, false otherwise
	'''

	# Get all groups that this graph is shared with
	groups = get_all_groups_for_this_graph(graph_owner, graphname)

	# If there are any groups that share this graph
	# check to see if the logged in user is a member in that group.
	# If they are, then they are allowed to see the graph
	if len(groups) > 0:
		for group in groups:
			
			# If logged in user owns a group that the graph is shared with
			if logged_in_user == group.owner_id:
				return True

			# Get all members of the group
			members = get_group_members(group.owner_id, group.group_id)

			# If the user is a member of a group that graph is shared with,
			# the user may view this graph
			for member in members:
				if logged_in_user == member.user_id:
					return True

	return None

def remove_group(owner, group):
	'''
		Removes a group from server.

		:param owner: Owner of group
		:param group: Group ID
		:return <result
	'''

	# Create database connection
	db_session = data_connection.new_session()

	# Get group
	group_get = db_session.query(models.Group).filter(models.Group.owner_id == owner).filter(models.Group.group_id == group).first()

	if group_get == None:
		return "Group not found"

	# Delete group
	db_session.delete(group_get)

	try:
		# Get group to graph 
		group_to_graph = db_session.query(models.GroupToGraph).filter(models.GroupToGraph.group_id == group).filter(models.GroupToGraph.group_owner == owner).all()

		# Delete entry from group to graph
		for gg in group_to_graph:
			db_session.delete(gg)
	except NoResultFound:
		print 'nothing found'

	try:
		# Get group to user 
		group_to_user = db_session.query(models.GroupToUser).filter(models.GroupToUser.group_id == group).filter(models.GroupToUser.group_owner == owner).all()

		# Delete entry from group to user
		for gu in group_to_user:
			db_session.delete(gu)
	except NoResultFound:
		print 'nothing found'

	db_session.commit()
	db_session.close()
	return "Successfully deleted " + group + " owned by " + owner + "."

def create_group(username, groupId):
	'''
		Inserts a uniquely named group under a username.

		:param owner: Owner of group
		:param groupId: Group ID
		:return <result>
	'''

	# Create database connection
	db_session = data_connection.new_session()

	# Check to see if group exists
	group = db_session.query(models.Group).filter(models.Group.group_id == cleanGroupName(groupId)).filter(models.Group.owner_id == username).first()

	# Group already exists in database
	if group != None:
		db_session.close()
		return None

	# Create new group
	new_group = models.Group(group_id = cleanGroupName(groupId), name = groupId, owner_id = username, description = "")

	# Add to database
	db_session.add(new_group)
	db_session.commit()
	db_session.close()
	return [groupId, cleanGroupName(groupId)]

def cleanGroupName(groupName):
	'''
		Cleans group name (gets rid of spaces and _ characters)

		:param groupName: Name of group
		:return group: cleaned group name
	'''
	groupName = groupName.replace(' ', '')
	groupName = groupName.replace('-', '')
	return groupName

def groups_for_user(username):
	'''
		Get all groups user belongs to or owns.

		:param username: Email of user
		:return Groups: [groups]
	'''
	# Create database connection
	db_session = data_connection.new_session()
	cleaned_group_data = []
	try:
		# Get all groups that the user is a member of
		member_of_groups = db_session.query(models.GroupToUser).filter(models.GroupToUser.user_id == username).all()

		# Appeend tuple that describes ID of group and the owner of the group
		for group in member_of_groups:
			cleaned_group_data.append({"groupId": group.group_id, "group_owner": group.group_owner})

	except NoResultFound:
		print "User is not a member of any groups"

	try:
		# Get all groups that the user owns
		owned_groups = db_session.query(models.Group).filter(models.Group.owner_id == username).all()
	
		# Appeend tuple that describes ID of group and the owner of the group
		for group in owned_groups:
			cleaned_group_data.append({"groupId": group.group_id, "group_owner": group.owner_id})

	except NoResultFound:
		print "User is not an owner of any groups"

	db_session.close()
	return cleaned_group_data

def search_result_for_graphs_in_group(uid, search_type, search_terms, db_session, groupOwner, groupId):
	'''
		Search method for the graphs in group page.
		Emulates search functionality in graphs page except for a particular group.

		@param uid: Logged in user
		@param search_type: Type of search (partial_search or full_search)
		@param search_terms: All terms being searched for
		@param db_session: Database connection
		@param groupOwner: Owner of group
		@param groupId: ID of group
	'''

	# If it is a search type that is not recognized, return empty list
	if search_type != 'partial_search' and search_type !=  'full_search':
		return []

	# Make into list if it is not a lsit
	if not isinstance(search_terms, list):
		search_terms = search_terms.split(',')

	# If there are any search terms
	if len(search_terms) > 0:

		# List to keep track of all matched graphs
		initial_graphs_from_search = []

		# Get connection to database
		data_session = data_connection.new_session()

		# Go through each search term, aggregating 
		# all graphs that match the specific search term
		for search_word in search_terms:
			# matched_graphs contains a list of all graphs that match the specific search term
			matched_graphs = []
			# First, we check to see if there are any graphs that have a graph name that matches the search term
			matched_graphs += find_all_graphs_containing_search_word_in_group(uid, search_type, search_word, data_session, groupOwner, groupId)

			# ":" indicates that search_word may be an edge
			if ':' in search_word:
				# append all graphs that contain an edge which matches the search_word
				matched_graphs += find_all_graphs_containing_edges_in_group(uid, search_type, search_word, data_session, groupOwner, groupId)
			# otherwise append all graphs that contain a node which matches the search word
			else:
				matched_graphs += find_all_graphs_containing_nodes_in_group(uid, search_type, search_word, data_session, groupOwner, groupId)

			# Go through all matched graphs
			# If there is a graph that appears multiple times in the list
			# combine their result.
			# Effectively, a graph may appear at most one time for each search word
			matched_graphs = combine_similar_graphs(matched_graphs)

			# Add condensed tuples to list of graphs matched
			initial_graphs_from_search += matched_graphs 

		# Go through and count the list of occurrences of matched graph
		graph_repititions = defaultdict(int)

		# Counting the number of occurences
		for graph_tuple in initial_graphs_from_search:
			key = graph_tuple[0] + graph_tuple[4]
			graph_repititions[key] += 1

		# Go through and aggregate all graph together
		graph_mappings = defaultdict(list)

		# If the number of times a graph appears matches the number of search terms
		# it is a graph we want (simulating the and operator for all search terms)
		for graph_tuple in initial_graphs_from_search:
			key = graph_tuple[0] + graph_tuple[4]

			graph_tuple = list(graph_tuple)

			# Placeholder for tags of the graph
			graph_tuple.insert(1, "")

			# Graph matches all search terms
			if graph_repititions[key] == len(search_terms):

				# If we haven't seen this graph yet 
				if key not in graph_mappings:
					graph_mappings[key] = tuple(graph_tuple)
				else:
					# Combine result of previous tuple
					old_tuple = list(graph_mappings[key])

					# If there is already a matching node/edge id
					if len(old_tuple[2]) > 0 and len(graph_tuple[2]) > 0:
						old_tuple[2] += ", " + graph_tuple[2]
						old_tuple[3] += ", " + graph_tuple[3]
					# Otherwise, simply insert this graph tuples id
					else:
						old_tuple[2] += graph_tuple[2]
						old_tuple[3] += graph_tuple[3]

					graph_mappings[key] = tuple(old_tuple)

		# Go through all the graphs and insert tags for the graphs that match all search terms
		return graph_mappings.values()
	else:
		return []

def find_all_graphs_containing_edges_in_group(uid, search_type, search_word, db_session, groupId, groupOwner):
	'''
		Finds all edges that match search terms that are shared with group.
		Emulates search functionality in graphs page except for a particular group.

		@param uid: Logged in user
		@param search_type: Type of search (partial_search or full_search)
		@param search_word: Term to search for in edge
		@param db_session: Database connection
		@param groupOwner: Owner of group
		@param groupId: ID of group
	'''
	# List to keep track of all graphs that contain edges that match the search_word
	initial_graphs_matching_edges = []

	# Separate the edge into its two node ID's
	# This is done because in the database, an edge ID is comprised of target:source nodes
	node_ids = search_word.split(":")

	# Get head and tail node references
	head_node = node_ids[0]
	tail_node = node_ids[1]

	# List of all head node ids
	head_nodes = []

	# List of all tail node ids
	tail_nodes = []

	# Match all edges that contain the edges that exactly match the search_word
	if search_type == "full_search":

		# Get all (head) nodes that contain a label matching search_word
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.label == head_node).all()
		
		# Get all (tail) nodes that contain a label matching search_word
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.label == tail_node).all()

		# Get all (head) nodes that contain a node id matching search_word 
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id == head_node).all()

		# Get all (tail) nodes that contain a node id matched search_word 
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id == tail_node).all()
		
	elif search_type == "partial_search":

		# Get all (head) nodes that contain a partially matching label
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.label.like("%" + head_node + "%")).all()
		
		# Get all (tail) nodes that contain a label partially matching label
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.label.like("%" + tail_node + "%")).all()

		# Get all (head) nodes that contain a node id partially matching search_word 
		head_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id.like("%" + head_node + "%")).all()
		
		# Get all (head) nodes that contain a node id partially matching search_word 
		tail_nodes += db_session.query(models.Node.node_id).filter(models.Node.node_id.like("%" + tail_node + "%")).all()

	# Remove all the duplicates
	head_nodes = list(set(head_nodes))
	tail_nodes = list(set(tail_nodes))

	# Go through head and tail nodes to see if there are any graphs
	# that match the given view type (my graphs, shared, public).
	# In other words, return all graphs that having matching edges
	# for the given view type.

	# TODO: ASK MURALI ABOUT BIDIRECTION EDGES

	# If there are both head and tail nodes
	if len(head_nodes) > 0 and len(tail_nodes) > 0:
		# Go through all permutations of these nodes
		# compile graphs that match the given view_type (my graphs, shared, public)
		for i in xrange(len(head_nodes)):
			for j in xrange(len(tail_nodes)):
				h_node =  head_nodes[i][0]
				t_node =  tail_nodes[j][0]
				
				# We make two queries because we want to have tail:head and head:tail search (to resolve undirected edges searching)
				initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.Edge.head_node_id == h_node).filter(models.Edge.tail_node_id == t_node).filter(models.Edge.graph_id == models.GroupToGraph.graph_id).filter(models.Edge.user_id == uid).filter(models.GroupToGraph.user_id == models.Edge.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()
				initial_graphs_matching_edges += db_session.query(models.Edge).filter(models.Edge.head_node_id == t_node).filter(models.Edge.tail_node_id == h_node).filter(models.Edge.graph_id == models.GroupToGraph.graph_id).filter(models.Edge.user_id == uid).filter(models.GroupToGraph.user_id == models.Edge.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

		graph_dict = dict()
		# Remove duplicates for all graphs that match have the same edge matching search term
		for graph in initial_graphs_matching_edges:
			key = graph.head_node_id + graph.graph_id + graph.user_id + graph.tail_node_id + graph.edge_id
			if key in graph_dict:
				continue
			else:
				graph_dict[key] = graph

		return graph_dict.values()
	else:
		return []


def find_all_graphs_containing_nodes_in_group(uid, search_type, search_word, db_session, groupId, groupOwner):
	'''
		Finds all nodes that match search terms that are shared with group.
		Emulates search functionality in graphs page except for a particular group.

		@param uid: Logged in user
		@param search_type: Type of search (partial_search or full_search)
		@param search_word: Term to search for in node
		@param db_session: Database connection
		@param groupOwner: Owner of group
		@param groupId: ID of group
	'''
	node_data = []

	# If we only want partially matched nodes
	if search_type == 'partial_search':

		# Get all nodes that have a partially matching label
		node_data = db_session.query(models.Node).filter(models.Node.label.like("%" + search_word + "%")).filter(models.Node.graph_id == models.GroupToGraph.graph_id).filter(models.GroupToGraph.user_id == models.Node.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

		# Get all nodes that have a partially matching node id
		node_data += db_session.query(models.Node).filter(models.Node.node_id.like("%" + search_word + "%")).filter(models.Node.graph_id == models.GroupToGraph.graph_id).filter(models.GroupToGraph.user_id == models.Node.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()
	else:
		# Get all nodes that have an exact matching label
		node_data = db_session.query(models.Node).filter(models.Node.label == search_word).filter(models.Node.graph_id == models.GroupToGraph.graph_id).filter(models.GroupToGraph.user_id == models.Node.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()
	
		# Get all nodes that have an exact matching node id
		node_data += db_session.query(models.Node).filter(models.Node.node_id == search_word).filter(models.Node.graph_id == models.GroupToGraph.graph_id).filter(models.GroupToGraph.user_id == models.Node.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

	graph_dict = dict()

	# Remove duplicates for all graphs that match have the same node id and label matching search term
	for graph in node_data:
		key = graph.graph_id + graph.user_id + graph.label + graph.node_id
		if key in graph_dict:
			continue
		else:
			graph_dict[key] = graph

	return graph_dict.values()

def find_all_graphs_containing_search_word_in_group(uid, search_type, search_word, db_session, groupId, groupOwner):
	'''
		Finds all graphs with names that match search terms that are shared with group.
		Emulates search functionality in graphs page except for a particular group.

		@param uid: Logged in user
		@param search_type: Type of search (partial_search or full_search)
		@param search_word: Term to search for in graph name
		@param db_session: Database connection
		@param groupOwner: Owner of group
		@param groupId: ID of group
	'''
	matched_graphs = []
	# Return all graphs that have a graph name that partially matches the search word
	if search_type == 'partial_search':
		try:
			#Get all graphs that have ID that partially match search term
			matched_graphs = db_session.query(models.Graph).filter(models.Graph.graph_id.like("%" + search_word + "%")).filter(models.GroupToGraph.graph_id == models.Graph.graph_id).filter(models.GroupToGraph.user_id == models.Graph.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

		except NoResultFound:
			print "No shared graphs matching search term"

	elif search_type == 'full_search':
		try:
			# Return all graphs that have a graph name that exactly matches the search word
			matched_graphs = db_session.query(models.Graph).filter(models.Graph.graph_id == search_word).filter(models.GroupToGraph.graph_id == models.Graph.graph_id).filter(models.GroupToGraph.user_id == models.Graph.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

		except NoResultFound:
			print "No shared graphs matching search term"


	graph_dict = dict()

	# Remove duplicates for all graphs that match have the same graph matching search term
	for graph in matched_graphs:
		key = graph.graph_id + graph.user_id
		if key in graph_dict:
			continue
		else:
			graph_dict[key] = graph

	return graph_dict.values()

def tag_result_for_graphs_in_group(groupOwner, groupId, tag_terms, db_session):
	'''
		Finds all graphs with graphs that have matching tag.

		@param groupOwner: Owner of group
		@param groupId: ID of group
		@param tag_terms: Tag terms to search for
		@param db_session: Database connection
	'''
	intial_graphs_with_tags = []

	if len(tag_terms) > 0:
		for tag in tag_terms:
			try:
				# Find graphs that have tag being searched for
				intial_graphs_with_tags += db_session.query(models.Graph).filter(models.Graph.graph_id == models.GraphToTag.graph_id).filter(models.Graph.user_id == models.GraphToTag.user_id).filter(models.GraphToTag.tag_id == tag).filter(models.GroupToGraph.graph_id == models.Graph.graph_id).filter(models.GroupToGraph.user_id == models.Graph.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

			except NoResultFound:
				print "No shared graphs with tag"

		# Go through and count the list of occurrences of matched graph
		graph_repititions = defaultdict(int)

		# Counting the number of occurences
		for graph in intial_graphs_with_tags:
			graph_repititions[graph] += 1

		# Go through and aggregate all graph together
		graph_mappings = defaultdict(list)

		# If the number of times a graph appears matches the number of search terms
		# it is a graph we want (simulating the and operator for all search terms)
		for graph in intial_graphs_with_tags:

			graph_tuple = (graph.graph_id, get_all_tags_for_graph(graph.graph_id, graph.user_id), graph.modified, graph.user_id, graph.public)

			# Graph matches all search terms
			if graph_repititions[graph] == len(tag_terms):

				# If we haven't seen this graph yet 
				if graph not in graph_mappings:
					graph_mappings[graph] = graph_tuple
				
		# Go through all the graphs and insert tags for the graphs that match all search terms
		return graph_mappings.values()
	else:
		return []

def get_all_graphs_for_group(uid, groupOwner, groupId, request):
	'''
		Get all graphs that belong to this group.

		:param groupOwner: Owner of group
		:param groupId: Id of group
		:param search_terms: Terms to be searched for
		:param tag_terms: Tags to be searched for in graphs
		:return Graphs: [graphs]
	'''

	# Get connection to databse
	db_session = data_connection.new_session()

	# Set search type
	search_type = None

	if 'partial_search' in request.GET:
		search_type = 'partial_search'
	elif 'full_search' in request.GET:
		search_type = 'full_search'

	# Check to see if query has search terms, tag terms, or 
	# user wants to sort graphs
	search_terms = request.GET.get(search_type)
	tag_terms = request.GET.get('tags') or request.GET.get('tag')
	order_by = request.GET.get('order')

	graph_data = []

	if tag_terms and len(tag_terms) > 0:
		cleaned_tags = tag_terms.split(',')
		# Goes through each tag, making it a string
		# so the url will contain those tags as a part
		# of the query string
		for tags in xrange(len(cleaned_tags)):
		    cleaned_tags[tags] = cleaned_tags[tags].strip()
		    # If user enters in a blank tag, delete it
		    if len(cleaned_tags[tags]) == 0:
		    	del cleaned_tags[tags]

 	if search_terms and len(search_terms) > 0:

		# Split up search terms by comma
		cleaned_search_terms = search_terms.split(',')

		# Goes through each search term, making it a string
		# so the url will contain those searches as a part
		# of the query string
		for i in xrange(len(cleaned_search_terms)):
			cleaned_search_terms[i] = cleaned_search_terms[i].strip()
			# Deleted no length search terms
			if len(cleaned_search_terms[i]) == 0:
				del cleaned_search_terms[i]

	# If both a tag term and search term are entered
	if search_terms and tag_terms and len(search_terms) > 0 and len(tag_terms) > 0:
		actual_graphs = []

		# Get all graphs that contain all the search terms
		search_result_graphs = search_result_for_graphs_in_group(uid, search_type, cleaned_search_terms, db_session, groupId, groupOwner)
		
		# Get all graphs that contain all the tag terms
		tag_result_graphs = tag_result_for_graphs_in_group(groupOwner, groupId, cleaned_tags, db_session)

		tag_graphs = [x[0] for x in tag_result_graphs]
		actual = [x[0] for x in actual_graphs]

		# If it is not already part of final graphs returned, add it in
		for graph in search_result_graphs:
			if graph[0] in tag_graphs and graph[0] not in actual:
				actual_graphs.append(graph)

		graph_data = actual_graphs

	# If only search terms are entered
	elif search_terms:
		graph_data = search_result_for_graphs_in_group(uid, search_type, cleaned_search_terms, db_session, groupId, groupOwner)

	# If only tag terms are entered
	elif tag_terms:
		graph_data = tag_result_for_graphs_in_group(groupOwner, groupId, cleaned_tags, db_session)
	else:
		try:
			graph_data = db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.modified, models.GroupToGraph.user_id).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).all()

		except NoResultFound:
			print 'no result found'

	# If user wants to sort the data
	if order_by:
		graph_data = order_information(order_by, search_terms, graph_data)
	else:
		graph_data = order_information("modified_descending", search_terms, graph_data)

	db_session.close()
	return graph_data

def get_all_groups_for_user_with_sharing_info(graphowner, graphname):
	'''
		Gets all groups that a user owns or is a member of,
		and indicates whether the specified graph is shared with that group

		:param owner: Owner of graph
		:param grpahname: Name of graph
		:return group_info: [{group_name: <name of group>, "graph_shared": boolean}]
	'''
	group_info = []

	# Get all groups that the user is a member of or owns
	groups = get_groups_of_user(graphowner) + get_all_groups_with_member(graphowner)

	# Get connection to database
	db_session = data_connection.new_session()
	# Determine if a graph is shared with a specific group
	for group in groups:
		group_name = group[0]
		group_id = group[4]
		group_owner = group[2]

		# Check if graph is shared with this group
		is_shared_with_group = db_session.query(models.GroupToGraph).filter(models.GroupToGraph.graph_id == graphname).filter(models.GroupToGraph.user_id == graphowner).filter(models.GraphToTag.user_id == graphowner).filter(models.GroupToGraph.group_id == group_id).filter(models.GroupToGraph.group_owner == group_owner).first()

		# If it is not shared, then set "graph_shared" to False
		if is_shared_with_group == None:
				group_info.append({"group_name": group_name, "group_owner": group_owner, "group_id": group_id, "graph_shared": False})
		else:
				group_info.append({"group_name": group_name, "group_owner": group_owner, "group_id": group_id, "graph_shared": True})

	db_session.close()
	return group_info

def updateSharingInformationForGraph(owner, gid, groups_to_share_with, groups_not_to_share_with):
	'''
		Shares specified graph with all groups to share with.  Unshares specified graph with all groups to unshare with.
		:param owner: Owner of graph
		:param grpahname: Name of graph
		:param groups_to_share_with: Groups to share with ** have form of [groupName_groupOwner,....]
		:param groups_not_to_share_with: Groups not to share with ** have form of [groupName_groupOwner,....]
	'''
	for group in groups_to_share_with:
		groupInfo = group.split("12345__43121__")

	for group in groups_not_to_share_with:
		groupInfo = group.split("12345__43121__")
		unshare_graph_with_group(owner, gid, groupInfo[0], groupInfo[1])

def add_user_to_group(username, owner, group):
	'''
		Adds a user to a group.

		:param username: Username to add to group
		:param owner: Owner of the group
		:param group: Group ID
		:return <Status>
	'''
	# Create database connection
	db_session = data_connection.new_session()

	user = db_session.query(models.User).filter(models.User.user_id == username).first()

	if user == None:
		db_session.close()
		return "User does not exist!"

	# Is user a member of the group
	isMember = db_session.query(models.GroupToUser.user_id).filter(models.GroupToUser.user_id == owner).filter(models.GroupToUser.group_id == group).first()

	# Is user an owner of the group
	isOwner = db_session.query(models.Group.owner_id).filter(models.Group.owner_id == owner).filter(models.Group.group_id == group).first()

	message = ""

	# User must be an owner of a member of a group to add members to it
	if isMember != None or isOwner != None:
		new_group_member = models.GroupToUser(group_id = group, group_owner = owner, user_id = username)
		db_session.add(new_group_member)
		db_session.commit()
		message = "Successfully added user " + username + " to " + group + "."
	else:
		message = "Become the owner or a member of this group first!"

	db_session.close()
	return message

def remove_user_from_group(username, owner, groupId):
	'''
		Removes user from group.

		:param username: User to remove
		:param owner: Owner of group
		:param groupId: Group ID
		:return <status>
	'''

	# Create database connection
	db_session = data_connection.new_session()

	# Check to see if user exists
	user = db_session.query(models.User).filter(models.User.user_id == username).first()

	if user == None:
		db_session.close()
		return "User does not exist!"

	# Check to see if group exists
	group = db_session.query(models.Group).filter(models.Group.group_id == groupId).filter(models.Group.owner_id == owner).first()

	if group == None:
		db_session.close()
		return "Group does not exist!"

	# Check to see if member in that group actually exists
	group_member = db_session.query(models.GroupToUser).filter(models.GroupToUser.group_id == groupId).filter(models.GroupToUser.group_owner == owner).first()

	if group_member == None:
		db_session.close()
		return "Group member does not exist"

	db_session.delete(group_member)
	db_session.commit()
	db_session.close()
	return "Successfully removed user " + username + " from " + groupId + "."

def remove_user_through_ui(username, owner, group):
	'''
		Removes user from group through UI.

		:param username: User to remove
		:param owner: Owner of group
		:param group: Group ID
		:return <status>
	'''
	return remove_user_from_group(username, owner, group)

def share_graph_with_group(owner, graph, groupId, groupOwner):
	'''
		Shares a graph with group.
		
		:param owner: Owner of group
		:param graph: Graph to share 
		:param groupId: Group ID
		:param groupOwner: Group Owner
		:return <status>
	'''

	# Get graph
	graph_exists = get_graph(owner, graph)

	if graph_exists == None:
		return "Graph does not exist"

	# Create database connection
	db_session = data_connection.new_session()

	# Is graph already shared
	shared_graph = db_session.query(models.GroupToGraph).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).filter(models.GroupToGraph.graph_id == graph).filter(models.GroupToGraph.user_id == owner).first()

	# Graph is already shared
	if shared_graph != None:
		return None

	# Is a user a member of the group trying to share graph with
	group_member = db_session.query(models.GroupToUser).filter(models.GroupToUser.user_id == owner).filter(models.GroupToUser.group_id == groupId).filter(models.GroupToUser.group_owner == groupOwner).first()

	# Is a user the owner of a group
	group_owner = db_session.query(models.Group.owner_id).filter(models.Group.owner_id == groupOwner).filter(models.Group.group_id == groupId).first()

	# If they're an owner or a group member, they can add graph to the group
	if group_owner != None or group_member != None:
		new_shared_graph = models.GroupToGraph(group_id = groupId, group_owner = groupOwner, user_id = owner, graph_id = graph, modified = graph_exists.modified)

		db_session.add(new_shared_graph)
		db_session.commit()

	db_session.close()
	return None

def unshare_graph_with_group(owner, graph, groupId, groupOwner):
	'''
		Graph to unshare with group.

		:param owner: Owner of group
		:param graph: Graph to unshare 
		:param groupId: Group ID
		:param groupOwner: Group Owner
		:return <status>
	'''

	# Get graph
	graph_exists = get_graph(owner, graph)

	if graph_exists == None:
		return "Graph does not exist!"

	# Create database connection
	db_session = data_connection.new_session()

	# Is this graph already shared with the group?
	is_shared_with_group = db_session.query(models.GroupToGraph).filter(models.GroupToGraph.graph_id == graph).filter(models.GroupToGraph.user_id == owner).filter(models.GroupToGraph.group_id == groupId).filter(models.GroupToGraph.group_owner == groupOwner).first()

	# If graph is not shared with group
	if is_shared_with_group == None:
		db_session.close()
		return "Can't unshare a graph that is not currently shared with the group"

	# Unshare the graph
	db_session.delete(is_shared_with_group)
	db_session.commit()
	db_session.close()
	return None

# ---------------- END REST API ------------------------------

def view_graphs_of_type(view_type, username):
	'''
		View graphs of this type e.g. shared, my graphs, public.

		:param view_type: Type of view (shared, public)
		:param username: Name of user
		:return Graphs: [graphs]
	'''

	# Create database connection
	db_session = data_connection.new_session()

	graphs = []

	# Select graphs depending on view_type
	if view_type == "public":
		# Get all public graphs
		try:
			graphs = db_session.query(models.Graph.graph_id, models.Graph.modified, models.Graph.user_id).distinct(models.Graph.graph_id).filter(models.Graph.public == 1).all()
		except NoResultFound:
			print "No public graphs"

	elif view_type == "shared":
		try:
			graphs = db_session.query(models.GroupToGraph.graph_id, models.GroupToGraph.modified, models.GroupToGraph.user_id).distinct(models.GroupToGraph.graph_id, models.GroupToGraph.user_id, models.GroupToGraph.modified).filter(models.GroupToGraph.group_id == models.GroupToUser.group_id).filter(models.GroupToGraph.group_owner == models.GroupToUser.group_owner).filter(models.GroupToUser.user_id == username).all()
		except NoResultFound:
			print "No shared graphs"
	else:
		try:
			# Get all my graphs
			graphs = db_session.query(models.Graph.graph_id, models.Graph.modified, models.Graph.user_id).filter(models.Graph.user_id == username).all()
		except NoResultFound:
			print "No owned graphs"

	return graphs

	db_session.close()
	return cleaned_graphs

def is_public_graph(username, graph):
	'''
		Checks to see if a given graph for a user is public.

		:param username: Email of user
		:param graph: Graph of user
		:return boolean: True if public graph
	'''

	# Get the graph
	graph = get_graph(username, graph)

	# If no graph is found, return None
	if graph == None:
		return None

	# Return true if public, false otherwise
	if graph.public == 1:
		return True
	else:
		return False

def get_all_groups_for_this_graph(uid, graph):
	'''
		Gets all the groups that the graph is shared with.

		:param uid: User of the graph
		:param graph: Name of graph
		:return Groups: [groups]
	'''

	# Get database connection
	db_session = data_connection.new_session()

	try:
		# Get all groups that this graph is shared with
		shared_groups = db_session.query(models.Group).filter(models.GroupToGraph.graph_id == graph).filter(models.GroupToGraph.user_id == uid).filter(models.GroupToGraph.group_id == models.Group.group_id).filter(models.GroupToGraph.group_owner == models.Group.owner_id).all()
		db_session.close()
		return shared_groups
	except NoResultFound:
		db_session.close()
		return None

def change_graph_visibility(isPublic, user_id, graphName):
	'''
		Makes specified graph and all associated layouts public or private

		:param isPublic boolean that decides if graph is made public or private (0 if private, 1 if public)
		:param user_id ID of owner of graph
		:param graphName name of graph to make public
	'''

	# Create database connection
	db_session = data_connection.new_session()

	# Get the graph
	graph = db_session.query(models.Graph).filter(models.Graph.graph_id == graphName).filter(models.Graph.user_id == user_id).first()

	# If it doesn't exist
	if graph == None:
		db_session.close()
		return "Graph with name " + graphName + " doesn't exist under " + user_id + '.'

	# Update property
	graph.public = isPublic
	db_session.commit()

	try:
		# Change all layouts visibility for a graph
		layouts = db_session.query(models.Layout).filter(models.Layout.graph_id == graphName).filter(models.Layout.user_id == user_id).filter(models.Layout.shared_with_groups == 1).all()
		for layout in layouts:
			layout.public = isPublic
			db_session.commit()

	except NoResultFound:
		print 'No shared layouts for this graph'

	db_session.close()


# Changes the name of a layout
def changeLayoutName(uid, gid, old_layout_name, new_layout_name, loggedIn):
	'''
		Changes the name of the layout.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param old_layout_name: Old name of layout
		:param new_layout_name: New name of layout
		:param loggedIn: User making those changes
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Get the layout
	layout = db_session.query(models.Layout).filter(models.Layout.layout_name == old_layout_name).filter(models.Layout.owner_id == uid).filter(models.Layout.graph_id == gid).first()

	# Change the name
	if layout != None:
		layout.layout_name = new_layout_name
		db_session.commit()
		
	db_session.close()

def makeLayoutPublic(uid, gid, public_layout):
	'''
		Makes a layout public.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param public_layout: Name of layout
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Get layouts to make public
	layout = db_session.query(models.Layout).filter(models.Layout.layout_name == public_layout).filter(models.Layout.owner_id == uid).filter(models.Layout.graph_id == gid).first()
	
	# If layout exists, make it public
	if layout != None:
		if layout.public == 1:
			layout.public = 0

			# Get graph 
			graph = db_session.query(models.Graph).filter(models.Graph.graph_id == gid).filter(models.Graph.user_id == uid).first()

			# If layout isn't public, remove it as default id
			if graph != None:
				if graph.default_layout_id == layout.layout_id:
					graph.default_layout_id = None
		else:
			layout.public = 1

		db_session.commit()

	db_session.close()

def save_layout(layout_id, layout_name, owner, graph, user, json, public, shared_with_groups):
	'''
		Saves layout of specific graph.

		:param layout_id: Id of layout to save
		:param layout_name: Name of layout to save
		:param owner: Owner of the graph
		:param graph: Name of the graph
		:param user: user making those changes
		:param json: JSON of the graph
		:param public: Is layout public or not
		:param shared_with_groups: Is layout shared with groups
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# Checks to see if layout for graph already exists
	layout = db_session.query(models.Layout).filter(models.Layout.layout_name == layout_name).filter(models.Layout.owner_id == owner).filter(models.Layout.graph_id == graph).first()

	if layout != None:
		return "Layout with this name already exists for this graph! Please choose another name."

	# Add the new layout
	new_layout = models.Layout(layout_id = None, layout_name = layout_name, owner_id = owner, graph_id = graph, user_id = user, json = json, public = public, shared_with_groups = shared_with_groups)

	db_session.add(new_layout)
	db_session.commit()
	db_session.close()

def deleteLayout(uid, gid, layoutToDelete, loggedIn):
	'''
		Deletes layout from graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param layoutToDelete: name of layout to delete
		:param loggedIn: User that is deleting the graph
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get the specific layout
		layout = db_session.query(models.Layout).filter(models.Layout.layout_name == layoutToDelete).filter(models.Layout.owner_id == uid).filter(models.Layout.graph_id == gid).first()

		if layout == None:
			return None

		# Get graph which may contain a layout 
		graph = db_session.query(models.Graph).filter(models.Graph.graph_id == gid).filter(models.Graph.user_id == uid).first()

		if graph == None:
			return None

		# If layout being deleted is graphs default layout, remove both
		if graph.default_layout_id == layout.layout_id:
			graph.default_layout_id = None
			db_session.commit()

		db_session.delete(layout)
		db_session.commit()

		db_session.close()
		return None
	except Exception as ex:
		db_session.close()
		return ex

def get_layout_for_graph(layout_name, graph_id, graph_owner, loggedIn):
	'''
		Retrieves specific layout for a certain graph.

		:param layout_name: Name of layout
		:param layout_graph: Name of graph
		:param layout_owner: Owner of layout
		:param loggedIn: Logged in user
		:return Layout: [layout]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get layout for graph if it exists
		layout = db_session.query(models.Layout).filter(models.Layout.layout_name == layout_name).filter(models.Layout.graph_id == graph_id).filter(models.Layout.owner_id == graph_owner).one()

		db_session.close()
		return cytoscapePresetLayout(json.loads(layout.json))

	except NoResultFound:
		db_session.close()
		return None	

def cytoscapePresetLayout(csWebJson):
	'''
		Converts CytoscapeWeb preset layouts to be
		the standards of CytoscapeJS JSON. See http://js.cytoscape.org/#layouts/preset
		for more details.

		:param csWebJson: A CytoscapeWeb compatible layout json containing coordinates of the nodes
		:return csJson: A CytoscapeJS compatible layout json containing coordinates of the nodes
	'''

	csJson = {}

	# csWebJSON format: [{x: x coordinate of node, y: y coordinate of node, id: id of node},...]
	# csJson format: [id of node: {x: x coordinate of node, y: y coordinate of node},...]

	for node_position in csWebJson:
		csJson[str(node_position['id'])] = {
			'x': node_position['x'],
			'y': node_position['y']
		};

	return json.dumps(csJson)

def get_all_layouts_for_graph(uid, gid):
	'''
		Get all layouts for graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:return Layouts: [layouts of graph]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get layouts for graph 
		layouts = db_session.query(models.Layout).filter(models.Layout.owner_id == owner).filter(models.Layout.graph_id == gid).all()

		# Get rid of unicode
		cleaned_layouts = []
		for layout in layouts:
			cleaned_layouts.append(layout.layout_name)

		db_session.close()
		return layout

	except NoResultFound:
		db_session.close()
		return None	

def share_layout_with_all_groups_of_user(owner, gid, layoutId):
	'''
		Shares a layout with all the groups that owner of a graph is a part of.
		
		:param uid: Owner of graph
		:param gid: Name of graph
		:param layoutId: LayoutID of the graph
	'''
	# Create database connection
	db_session = data_connection.new_session()

	# If layout was the default graph layout, then we have to clear that entry
	graph = db_session.query(models.Graph).filter(models.Graph.user_id == owner).filter(models.Graph.graph_id == gid).first()

	if graph == None:
		return None

	# Get layout if it exists
	layout = db_session.query(models.Layout).filter(models.Layout.graph_id == gid).filter(models.Layout.layout_name == layoutId).first()

	if layout == None:
		return None

	# If the current layout is not shared with the group, share it
	if layout.shared_with_groups == 0:
		layout.shared_with_groups = 1
	else:
		# If it is shared, then unshare it
		layout.shared_with_groups = 0
		layout.public = 0

		# If layout to be unshared is a default layout
		# remove it as a default layout
		if graph.default_layout_id == layout.layout_id:
				graph.default_layout_id = None
				db_session.commit()
				
	print graph.default_layout_id
	db_session.commit()
	db_session.close()
	return None	

# Gets my layouts for a graph
def get_my_layouts_for_graph(uid, gid, loggedIn):
	'''
		Get my layouts for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param loggedIn: Current user of graphspace
		:return Layouts: [my layouts of graph]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get all layouts for graph that user created
		layouts = db_session.query(models.Layout.layout_name).filter(models.Layout.owner_id == uid).filter(models.Layout.graph_id == gid).filter(models.Layout.user_id == loggedIn).filter(models.Layout.shared_with_groups == 0).filter(models.Layout.public == 0).all()

		cleaned_layouts = []

		for layout_name in layouts:
			cleaned_layouts += layout_name
		db_session.close()
		return cleaned_layouts

	except NoResultFound:
		db_session.close()
		return None

def get_shared_layouts_for_graph(uid, gid, loggedIn):
	'''
		Get shared layouts for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param loggedIn: Current user of graphspace
		:return Layouts: [shared layouts of graph]
	'''

	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Get all groups this graph is shared with
		all_groups_for_graph = get_all_groups_for_this_graph(uid, gid)

		# Get all groups that the user is a member of
		all_groups_for_user = get_all_groups_with_member(loggedIn, skip = True)

		cleaned_layout_names = []

		group_dict = dict()

		# Get all groups shared with this graph, removing all duplicates
		for group in all_groups_for_graph:
			key = group.group_id + group.owner_id

			if key not in group_dict:
				group_dict[key] = group

		# Get all groups that the user can see
		for group in all_groups_for_user:
			key = group.group_id + group.owner_id

			if key in group_dict:

				# If the current user is a member of any groups that have current graph shared in
				# for group in all_groups_for_graph:
				layout_names = db_session.query(models.Layout.layout_name).filter(models.Layout.owner_id == uid).filter(models.Layout.graph_id == gid).filter(models.Layout.shared_with_groups == 1).all()

				for name in layout_names:
					cleaned_layout_names += name

		db_session.close()
		return cleaned_layout_names
	except NoResultFound:
		db_session.close()
		return []

def get_my_shared_layouts_for_graph(uid, gid, loggedIn):
	'''
		Get shared layouts of the graph owner for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param loggedIn: Current user of graphspace
		:return Layouts: [shared layouts of graph]
	'''

	# Create database connection
	db_session = data_connection.new_session()

	try:
		# In the database, we define unlisted as the parameter to determine if a certain
		# layout is shared within all groups that the graph is shared with and 
		# public to determine whether everyone is allowed access to the layout.
		# If the graph is public, all shared layouts should be public as well, therefore
		# we collect all shared and public layouts.
		# Note: This is done as a second-measure step and it shouldn't ever matter
		# because all layouts are set to public when the graph is set to public
		shared_layouts_uncleaned = db_session.query(models.Layout.layout_name).distinct(models.Layout.layout_name).filter(models.Layout.owner_id == uid).filter(models.Layout.user_id == loggedIn).filter(models.Layout.graph_id == gid).filter(or_(models.Layout.shared_with_groups == 1, models.Layout.public == 1)).all()

		# Get rid of unicode
		shared_layouts = []
		for shared_layout in shared_layouts_uncleaned:
			shared_layouts.append(shared_layout[0])

		db_session.close()
		return shared_layouts
	except NoResultFound:
		db_session.close()
		return None

def get_public_layouts_for_graph(uid, gid):
	'''
		Get public layouts for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:return Layouts: [public layouts of graph]
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		public_layouts = []

		# Get all the public layouts for a specific graph
		public_layout_uncleaned = db_session.query(models.Layout.layout_name).filter(models.Layout.owner_id == uid).filter(models.Layout.graph_id == gid).filter(models.Layout.public == 1).all()

		# Go through and remove the unicode
		for public_layout in public_layout_uncleaned:
			public_layouts.append(public_layout[0])

		db_session.close()
		return public_layouts
	except NoResultFound:
		db_session.close()
		return []

def get_all_graphs_for_tags(tags):
	'''
		Get all graphs that match the tags.

		:param tags: [List of tags to match]
		:return Graphs: [graphs that contain these tags]
	'''

	# Split tags into a list
	if tags:
		tag_terms = tags.split(',')
		for i in xrange(len(tag_terms)):
			tag_terms[i] = tag_terms[i].strip()

		# Create database connection
		db_session = data_connection.new_session()

		try:
			graph_list = []
			actual_graphs_for_tags_list = []

			# Go through each individual tag
			for tag in tag_terms:
				# Get all graphs that contain the specific tag we are searching for
				graph_list += db_session.query(models.Graph.graph_id).distinct(models.Graph.graph_id).filter(models.GraphToTag.tag_id == tag).filter(models.GraphToTag.graph_id == models.Graph.graph_id).all()

			# Get number of times the graph names appear.
			# If they appear the same number of times as the lenght of the tag terms
			# it implicitly means that the graph has all of the tags that are being searched for.
			accurate_tags = Counter(graphs_for_tag_list)
			for graph in graphs_for_tag_list:
				if accurate_tags[graph] == len(tag_terms):
					actual_graphs_for_tags.append(graph[0])

			db_session.close()
			return actual_graphs_for_tags

		except NoResultFound:
			db_session.close()
			return None
	else:
		return None

def get_all_tags_for_user(username):
	'''
		Return all tags that a user has for their graphs.

		:param username: Email of user in GraphSpace
		:return Tags: [tags]
	'''
	# Get database connection
	db_session = data_connection.new_session()

	try:
		# Get tags that the user has and return them
		tag_list = db_session.query(models.GraphToTag.tag_id).distinct(models.GraphToTag.tag_id).filter(models.GraphToTag.user_id == username).all()

		cleaned_tag_list = []

		# Get string from unicode so that I can parse it easier
		for tag in tag_list:
			cleaned_tag_list.append(str(tag[0]))

		db_session.close()
		return cleaned_tag_list
	except NoResultFound:
		db_session.close()
		return None

def get_all_tags_for_graph(graphname, username):
	'''
		Returns all of the tags for a specific graph.
	
		:param graphname: Name of graph to search for
		:param username: Email of user in GraphSpace
		:return Tags: [tags of graph]
	'''
	# Get database connection
	db_session = data_connection.new_session()

	try:
		# Retrieves all tags that match a given graph
		tag_list = db_session.query(models.GraphToTag.tag_id).distinct(models.GraphToTag.tag_id).filter(models.GraphToTag.user_id == username).filter(models.GraphToTag.graph_id == graphname).all()
		
		cleaned_tag_list = []

		# Get string from unicode so that I can parse it easier
		for tag in tag_list:
			cleaned_tag_list.append(str(tag[0]))

		db_session.close()
		return cleaned_tag_list
	except NoResultFound:
		db_session.close()
		return None

def change_graph_visibility_for_tag(isPublic, tagname, username):
	'''
		Makes all graphs under a tag owned by username public.

		:param isPublic: If graphs are to be made public (0 for private, 1 for public)
		:param tagname: Name of tag to search for
		:param username: Email of user in GraphSpace
		:return <Message>
	'''
	# Get database connection
	db_session = data_connection.new_session()

	try:
		# Get all the graphs that user OWNS which contain the matched tags
		# Note: Two people using same tag don't have to worry about their 
		# graphs changing visiblity because we only change the visibility 
		# of the graph the person is making the request owns

		# Go through all these graphs and change their public column. 
		# This means that they are visible or private depending on the boolean bit
		# associated in their public column (See Graph table)
		graph_list = db_session.query(models.Graph).filter(models.GraphToTag.tag_id == tagname).filter(models.GraphToTag.user_id == username).filter(models.Graph.user_id == username).filter(models.Graph.graph_id == models.GraphToTag.graph_id).all()

		for graph in graph_list:
			graph.public = isPublic

		# Go through all these nodes for graphs and change their public column. 
		# This means that they are visible or private depending on the boolean bit
		# associated in their public column (See Graph table)
		# NOTE: I had this originally, but is this even necessary?
		node_list = db_session.query(models.Node).filter(models.GraphToTag.tag_id == tagname).filter(models.GraphToTag.user_id == username).filter(models.Node.user_id == username).filter(models.Node.graph_id == models.GraphToTag.graph_id).all()

		# Change the visibility of all the layouts that are associated with a graph
		layout_list = db_session.query(models.Layout).filter(models.GraphToTag.tag_id == tagname).filter(models.GraphToTag.user_id == username).filter(models.Layout.user_id == username).filter(models.Layout.graph_id == models.GraphToTag.graph_id).all()

		for layout_graph in layout_list:
			layout_graph.public = isPublic

		db_session.commit()
		db_session.close()
	except NoResultFound:
		print "No graphs that match those tags for the user"
		db_session.close()
		return None

def delete_all_graphs_for_tag(tagname, username):
	'''
		Deletes all graphs under a tag owned by username.

		:param tagname: Name of tag to search for
		:param username: Email of user in GraphSpace
		:return <Message>
	'''
	# Create connection to database
	db_session = data_connection.new_session()

	try:
		# Get all the graphs that the user owns which match the tag
		graph_list = db_session.query(models.Graph).filter(models.GraphToTag.tag_id == tagname).filter(models.GraphToTag.user_id == username).filter(models.Graph.graph_id == models.GraphToTag.graph_id).filter(models.Graph.user_id == models.GraphToTag.user_id).all()

		# Delete all these graphs from the graphs table
		for graph in graph_list:
			db_session.delete(graph)

		# Get all the rows in graph_to_tag that the user owns
		delete_tags = db_session.query(models.GraphToTag).filter(models.GraphToTag.tag_id == tagname).filter(models.GraphToTag.user_id == username).all()

		# Delete all those rows from graph_to_tag database
		for tag_to_delete in delete_tags:
			db_session.delete(tag_to_delete)

		db_session.commit()
		db_session.close()
		return "Done"
	except Exception as ex:
		print ex
		db_session.close()
		return None

def getGraphInfo(uid, gid):
	'''
		Returns the json, visibility, and Id of the graph.

		:param uid: Owner of graph
		:param gid: Graph Id

		:return json, visibility, graph_id 
	'''

	# Create connection with database
	db_session = data_connection.new_session()

	try:
		# Retrieves json, public (visibility), and graph id of graph
		data = db_session.query(models.Graph.json, models.Graph.public, models.Graph.graph_id).filter(models.Graph.graph_id == gid).filter(models.Graph.user_id == uid).one()
		db_session.close()
		return data
	except Exception as ex:
		print ex
		db_session.close()
		return None

def retrieveJSON(uid, gid):
	'''
		Retrieves JSON of graph.

		:param uid: Graph owner
		:param gid: Graph Id

		:return JSON
	'''
	# Create connection with database
	db_session = data_connection.new_session()

	try:
		# Returns json if it exists, otherwise nothing
		data =  db_session.query(models.Graph.json).filter(models.Graph.user_id == uid).filter(models.Graph.graph_id == gid).one()
		db_session.close()
		return data
	except Exception as ex:
		print "No JSON found for " + gid
		print "Error " + ex
		db_session.close()
		return None

def insert_user(user_id, password, admin):
	'''
		Inserts user into database if they do not exist.

		:param user_id: Email of user
		:param password: Password of user
		:param admin: is user an admin?

		:return None if user already exists
	'''
	# Create database connection
	db_session = data_connection.new_session()

	try:
		# Creates a new user with given information
		new_user = models.User(user_id=user_id, password = password, admin = admin)
		db_session.add(new_user)
		db_session.commit()
		db_session.close()
	except Exception as ex:
		# If user already exists, don't create another user with same email
		print ex
		db_session.close()
		return None

def usernameMismatchError():
	'''
		Returns response telling user that their usernames (from the URL and username field in POST request)
		do not match
	'''
	return throwError(400, "Usernames do not match!")

def userNotFoundError():
	'''
		Returns response telling user that their username and password combination is not found.
	'''
	return throwError(401, "Username/Password is not recognized!")

def throwError(statusCode, error):
	'''
		Returns response to any error.
	'''
	return constructResponse(statusCode, None, error)

def sendMessage(statusCode, message):
	'''
		Returns response to sucessful request.
	'''
	return constructResponse(statusCode, message, None)

def constructResponse(statusCode, message, error):
	'''
		Constructs a response to send to the user.

		:param statusCode: Status coe of the request
		:param message: Message to send to the user
		:param error: Error to display to the user
		:return <Message>
	'''
	response = {"StatusCode": statusCode}

	if message != None:
		response['Message'] = message
	else:
		response['Error'] = error

	return response
