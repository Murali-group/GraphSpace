import sqlite3 as lite
from django.core.mail import send_mail
from datetime import datetime
import sys
import bcrypt
import json
from operator import itemgetter
from itertools import groupby
from collections import Counter, defaultdict
import random
import string
from django.conf import settings
import uuid

# Name of the database that is being used as the backend storage
DB_NAME = settings.DB_FULL_PATH
URL_PATH = settings.URL_PATH

# This file is a wrapper to communicate with sqlite3 database 
# that does not need authentication for connection

##################################################################
# This section contains methods to populate tables on startup



# --------------- Edge Insertions -----------------------------------


def assign_edge_ids(json_string):
	'''
		Modifies all id's of edges to be the names of the nodes that they are attached to.

		:param json_string: JSON of graph
		:return json_string: JSON of graph having id's for all edges
	'''

	
	ids = []
	# Appending id's to all the edges using the source and target as part of its ids
	# TODO: Change '-' character to something that can't be found in an edge
	for edge in json_string['graph']['edges']:
		edge['data']['id'] = edge['data']['source'] + '-' + edge['data']['target']
		if edge['data']['id'] not in ids:
			ids.append(edge['data']['id'])
		else:
			counter = 0
			while edge['data']['id'] in ids:
				counter += 1
				edge['data']['id'] = edge['data']['id'] + str(counter)
			ids.append(edge['data']['id'])

	# Return JSON having all edges with ids
	return json_string

# Populates the edge table with edges from jsons
# already in the database
def insert_all_edges_from_json():
	'''
		Inserts all edges from the JSON into the database

	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		con.text_factory = str
		cur = con.cursor()
		# Get information from all graphs already in the database
		# QUERY EXAMPLE: select user_id, graph_id from graph
		cur.execute('select user_id, graph_id, json from graph')
		data = cur.fetchall()

		# If there is anything in the graph table
		if data != None:
			# Go through each Graph
			for j in data:
				cleaned_json = json.loads(j[2])
				# Since there are two types of JSON: one originally submitted
				# We have to check to see if it is compatible with CytoscapeJS, if it isn't we convert it to be
				# TODO: Remove conversion by specifying it when the user creates a graph
				if 'data' in cleaned_json['graph']:
					cleaned_json = assign_edge_ids(json.loads(convert_json(j[2])))
				else:
					cleaned_json = assign_edge_ids(cleaned_json)
				
				print 'Processing %s of %s', (j[1], j[0])
				# Go through json of the graphs, if edge is not in database, then insert it (to avoid conflicts where source and target nodes are the same).
				# Special accomodation is done for if edge has directed property or not
				# TODO: Remove dependency of same source and target nodes as well as directed and undirected nodes
				for edge in cleaned_json['graph']['edges']:
					# TODO: Write query examples
					# QUERY EXAMPLE: select * from edge where head_user_id=? and head_graph_id = ? and head_id = ? and tail_user_id = ? and tail_graph_id = ? and tail_id = ?, (test_user@test.com, test_graph, {graph: ...})
					cur.execute('select * from edge where head_user_id=? and head_graph_id = ? and head_id = ? and tail_user_id = ? and tail_graph_id = ? and tail_id = ?', (j[0], j[1], edge['data']['source'], j[1], j[1], edge['data']['target']))
					sanity = cur.fetchall()
					if sanity == None or len(sanity) == 0:
						if 'target_arrow_shape' in edge['data']:
							# A normal edge has an edge and a tail.  However, we define as edge having a source and a target. source---->target
							# TODO: Double check Edge insertion values and write query examples
							cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (j[0], j[1], edge['data']["source"], j[1], j[1], edge['data']["target"], edge['data']["source"] + "-" + edge['data']["target"], edge['data']["target_arrow_shape"]))
						else:
							cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (j[0], j[1], edge['data']["source"], j[1], j[1], edge['data']["target"], edge['data']["source"] + "-" + edge['data']["target"], ""))

				cleaned_json_string = json.dumps(cleaned_json, sort_keys=True, indent=4)
				# Update original JSON to match that with the new edge ID's
				# TODO: Write query examples
				cur.execute('update graph set json=? where graph_id=? and user_id=?', (cleaned_json_string, j[1], j[0]))
				con.commit()

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

# --------------- End Edge Insertions --------------------------------
# Populates the edge table with edges from jsons
# already in the database
def update_json_to_cs_2_4():
	'''
		Inserts all edges from the JSON into the database

	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		con.text_factory = str
		cur = con.cursor()
		# Get information from all graphs already in the database
		# QUERY EXAMPLE: select user_id, graph_id from graph
		cur.execute('select user_id, graph_id, json from graph')
		data = cur.fetchall()

		# If there is anything in the graph table
		if data != None:
			# Go through each Graph
			for j in data:
				print 'Processing %s of %s', (j[1], j[0])
				cleaned_json = json.loads(j[2])
				# Since there are two types of JSON: one originally submitted
				# We have to check to see if it is compatible with CytoscapeJS, if it isn't we convert it to be
				# TODO: Remove conversion by specifying it when the user creates a graph
				if 'data' in cleaned_json['graph']:
					cleaned_json = update_json(json.loads(convert_json(j[2])))
				else:
					cleaned_json = update_json(cleaned_json)

				cleaned_json_string = json.dumps(cleaned_json, sort_keys=True, indent=4)
				# Update original JSON to match that with the new edge ID's
				# TODO: Write query examples
				cur.execute('update graph set json=? where graph_id=? and user_id=?', (cleaned_json_string, j[1], j[0]))
				con.commit()

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def update_json(json_string):

	for node in json_string['graph']['nodes']:
		# Replace label with content
		if 'label' in node['data']:
			node['data']['content'] = node['data']['label']
			del node['data']['label']

		#Replace color with background_color
		if 'color' in node['data']:
			node['data']['background_color'] = node['data']['color']
			node['data']['color'] = 'black'

		# Add text-wrap property
		node['data']['text_wrap'] = 'wrap'

		# Make it so text is vertically aligned
		node['data']['text_valign'] = 'center'

	for edge in json_string['graph']['edges']:
		# Replace label with content
		if 'label' in edge['data']:
			edge['data']['content'] = edge['data']['label']
			del edge['data']['label']

		# Replace shape with target_arrow_shape
		if 'directed' in edge['data']:
			edge['data']['target_arrow_shape'] = "triangle"

		# if 'target_arrow_shape' in edge['data']:
		# 	edge['data']['target_arrow_shape'] = "triangle"

	return json_string

def convert_json(original_json):
    '''
        Converts original_json that's used in Cytoscape Web
        such that it is compatible with the new Cytoscape.js

        See: http://cytoscape.github.io/cytoscape.js/

        Original json structure used for Cytoscape Web:
        {
            "metadata": {

            },

            "graph": {
                "data": {
                    "nodes": [ 
                        { "id": "node1", "label": "n1", ... },
                        { "id": "node2", "label": "n2", ... },
                        ...
                    ],
                    "edges": [ 
                        { "id": "edge1", "label": "e1", ... },
                        { "id": "edge2", "label": "e2", ... },
                        ...
                    ]
                }
            }
        }

        New json structure:
        {
            "metadata": {

            },

            "graph": {
                "nodes": [
                    {"data": {"id": "node1", "label": "n1", ...}},
                    {"data": {"id": "node2", "label": "n2", ...}},
                    ...
                ],
                "edges": [
                    {"data": {"id": "edge1", "label": "e1", ...}},
                    {"data": {"id": "edge2", "label": "e2", ...}},
                    ...
                ]
            }
        }
    '''

    #parse old json data
    old_json = json.loads(original_json)
    old_nodes = old_json['graph']['data']['nodes']
    old_edges = old_json['graph']['data']['edges']

    new_nodes, new_edges = [], []

    #format node and edge data
    for node in old_nodes:
        new_nodes.append({"data": node})

    for edge in old_edges:
        new_edges.append({"data": edge})

    #build the new json
    new_json = {}
    new_json['metadata'] = old_json['metadata']
    new_json['graph'] = {}
    new_json['graph']['nodes'] = new_nodes
    new_json['graph']['edges'] = new_edges

    return json.dumps(new_json, indent=4)

def add_everyone_to_password_reset():
	'''
		Adds all users to password reset table (cold-start).
		Only use this once so we know crypto algorithm used 
		for forgot password functionalities

	'''
	con = None
	try: 
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select user_id from user')

		user_data = cur.fetchall()

		for user in user_data:
			add_user_to_password_reset(user[0])

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def reUploadInconsistentGraphs(data):
	con = None
	try: 
		con = lite.connect(DB_NAME)
		cur = con.cursor()
		for graph in data:

			graph_id = graph[0]
			user_id = graph[1]
			graph_json = json.loads(graph[2])
			created = graph[3]
			modified = graph[4]
			public = graph[5]
			unlisted = graph[6]
			default_layout_id = graph[7]

			if 'data' in graph_json:
				graph_json = json.loads(convert_json(graph[2]))

			node_list = []
			edge_list = []

			for node in graph_json['graph']['nodes']:
				node_list.append(str(node['data']['id']))

			for edge in graph_json['graph']['edges']:
				edge_list.append(str(edge['data']['id']))

			cur.execute('select node_id from node where graph_id=? and user_id =?', (graph_id, user_id))

			nodes = cur.fetchall()

			mark_for_deletion = False

			if len(nodes) != len(node_list):
				print "Nodes don't match"
				mark_for_deletion = True

			for node in nodes:
				node = str(node[0])
				if node not in node_list:
					print "Unspecified node: ", node
					mark_for_deletion = True

			cur.execute('select head_id, tail_id from edge where head_user_id = ? and head_graph_id=?', (user_id, graph_id))

			edges = cur.fetchall()
			parsed_edges = []

			# if len(edges) != len(edge_list):
			# 	"Edges don't match"
			# 	mark_for_deletion = True

			for edge in edges:
				parsed_edges.append(str(edge[0]) + "-"+ str(edge[1]))

			for edge in edge_list:
				if edge not in parsed_edges:
					print "Unspecified edge: ", edge
					mark_for_deletion = True
				
			if mark_for_deletion == True:
				cur.execute('delete from graph where graph_id = ? and user_id = ?', (graph_id, user_id))
				cur.execute('delete from node where graph_id = ? and user_id = ?', (graph_id, user_id))
				cur.execute('delete from edge where head_graph_id = ? and head_user_id = ?', (graph_id, user_id))
				cur.execute('delete from graph_to_tag where graph_id=? and  user_id=?', (graph_id, user_id))
				con.commit()
				result = insert_graph(user_id, graph_id, graph[2], created=created, modified=modified, public=public, unlisted=unlisted, default_layout_id=default_layout_id, skip=True)
				if result != None:
					print result
				else:
					print "Reinserted: " + graph_id

		print "Done processing"

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

		cur.execute('select * from graph where public = 1')
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
##################################################
# This section contains methods to validate JSON 
def validate_json(jsonString):
	'''
		JSON Validator. Tells if the graph being inserted is 
		valid (CytoscapeJS will render it properly).  If not, 
		it throws an Error

		:param jsonString: JSON of the graph
		:return Errors | None: [Errors of JSON]
	'''

	req_error = validate_required_properties(jsonString)
	return req_error

def validate_required_properties(jsonString):
	# Validates the JSON that is uploaded to make sure
	# it has the following properties
	# node:
	# content,
	# id have to be unique

	# edge:
	# (dont need an id) - I auto generate one
	# source
	# target

	edge_properties = ['source', 'target']
	node_properties = ['content', 'id']

	try: 
		cleaned_json = json.loads(jsonString)
		# Since there are two types of JSON: one originally submitted
		if 'data' in cleaned_json['graph']:
			cleaned_json = json.loads(convert_json(jsonString))

		edges = cleaned_json['graph']['edges']
		nodes = cleaned_json['graph']['nodes']

		jsonErrors = ""
		# Combines edge and node Errors
		nodeError = propertyInJSON(nodes, node_properties, 'node')
		edgeError = propertyInJSON(edges, edge_properties, 'edge')

		# If any of the above errors has > 0 length, we have an error
		if len(nodeError) > 0:
			return nodeError
		if len(edgeError) > 0:
			return edgeError

		# We have to check to see if it is compatible with CytoscapeJS, if it isn't we convert it to be
		# TODO: Remove conversion by specifying it when the user creates a graph
		cleaned_json = assign_edge_ids(cleaned_json)

		nodeUniqueIDError = checkUniqueID(nodes)
		nodeCheckShape = checkShapes(nodes)

		if len(nodeUniqueIDError) > 0:
			return nodeUniqueIDError
		if len(nodeCheckShape) > 0:
			return  nodeCheckShape

		return None
	except ValueError, e:
		return e.args[0]

def checkUniqueID(elements):
	'''
		Checks to see if all of the elements in the json 
		have unique ids

		:param elements: JSON of nodes or edges
		:return Error | None: <ID for node has been dupliated!>
	'''
	id_map = []

	for element in elements:
		if element['data']['id'] not in id_map:
			id_map.append(element['data']['id'])
		else:
			return element['data']['id'] + " for a node is duplicated!"

	return ""

def checkShapes(elements):
	'''
		Checks to see if the shapes for node are valid shapes

		:param elements: JSON of nodes
		:return Error: <message>
	'''
	allowed_shapes = ["rectangle", "roundrectangle", "ellipse", "triangle", "pentagon", "hexagon", "heptagon", "octagon", "star", "diamond"]

	for element in elements:
		if element['data']['shape'] not in allowed_shapes:
			return "illegal shape: " + element['data']['shape'] + ' for a node'

	return ""

def propertyInJSON(elements, properties, elementType):
	'''
		Checks to see if the elements in the graph JSON (nodes and edges)
		adhere to the properties of CytoscapeJS (ie unique ids, valid shapes)

		:param elements: JSON of the elements (nodes or edges)
		:param properties: set of properties that element JSON should following
		:param elementType: Type of element it is (either node or edge)
		:return Error|None: <Property x not in JSON for element | node>
	'''

	for element in elements:
		met_all_properties = []

		element_data = element['data']
		for element_property in properties:
			if element_property not in element_data:
				if 'id' in element_data:
					return "Property '" + element_property +  "' not in JSON for " + elementType + ': ' + element_data['id']
				else:
					return "Property '" + element_property +  "' not in JSON for " + elementType
		
			met_all_properties.append(element_property)

	return ""



########### END JSON CHECKING #####################################

def add_user_to_password_reset(email):
	'''
		Adds a specific user to password_reset table.
		If email is in this, it automatically sends email to change 
		password for that account the next time the user logs on

		:param email: Email of the user for GraphSpace
	'''

	con = None
	try: 
		# If email is an account on GraphSpace
		if emailExists(email) != None:
			con = lite.connect(DB_NAME)
			cur = con.cursor()

			cur.execute('select user_id from password_reset where user_id=?', (email, ))

			user_data = cur.fetchall()

			# If user isn't already in password_reset table, add them with a new code
			if len(user_data) == 0:

				code = id_generator()
				# Generate a random code - used as the GET path to reset that user's password
				cur.execute('insert into password_reset values(?,?,?,?)', (None, email, code, datetime.now()))

				con.commit()

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def need_to_reset_password(email):
	'''
		Checks to see if a user needs to reset their password.
		If email is in password_reset email, they do, otherwise, not.

		:param email: Email of the user in GraphSpace
	'''

	con = None
	try: 
		# If email is in database
		if emailExists(email) != None:
			con = lite.connect(DB_NAME)
			cur = con.cursor()

			# If email is in password_reset table
			cur.execute('select user_id from password_reset where user_id = ?', (email, ))

			user_exists = cur.fetchall()

			if len(user_exists) > 0:
				return True
			else:
				return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return True
	finally:
		if con:
			con.close()

def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
	'''
		Generates an unique alphanumeric ID of specific size.

		:param size: Size of random string
		:param chars: Subset of characters to generate random string of
		:return string: Random string that adhere to the parameter properties
	'''
	return ''.join(random.choice(chars) for _ in range(size))

def is_admin(username):
	'''
		Checks to see if a given user is an admin

		:param username: Email of the user in GraphSpace
		:return boolean: True or False
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		#Execute query to check admin for username
		# TODO: Write query examples
		cur.execute('select admin from user where user_id = ?', (username,))
		data = cur.fetchone()

		# If user does exist and if his admin bit is set to 1, then they are an admin
		if data != None and data[0] == 1:
			return True
		else:
			# Return nothing otherwise
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def get_all_tags(username, view_type):
	'''
		Gets all tags for a given view_type and a username

		:param username: Email of the user in GraphSpace
		:param view_type: Type of view to filter (shared, public, owned)
		:return Tags: [] or None 
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Query only the tags that is the specfic view type
		# NOTE: Changes if a person is logged in
		if view_type == 'public' or username == None:
		# TODO: Write query examples
			cur.execute('select distinct gt.tag_id from graph_to_tag as gt, graph as g where g.public = 1 and gt.graph_id = g.graph_id limit 10')
		elif view_type == 'shared':
		# TODO: Write query examples
			cur.execute('select distinct gt.tag_id from graph_to_tag as gt, graph as g, group_to_graph as gg where gt.graph_id = g.graph_id and g.graph_id=gg.graph_id and gg.user_id=?limit 10', (username, ))
		else:
		# TODO: Write query examples
			cur.execute('select distinct gt.tag_id from graph_to_tag as gt, graph as g where gt.graph_id = g.graph_id and g.user_id=? limit 10', (username, ))

		# Get all the data, if there is any
		data = cur.fetchall()

		# If there is data, gather all of the tags for this view type and return it
		if data != None:
			cleaned_data = []
			for tag in data:
				if len(tag[0]) > 0:
					cleaned_data.append(tag[0])

			return cleaned_data
		else:
			# Otherwise return Noething
			return None
			
	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def get_valid_user(username, password):
	'''
		Checks to see if a user/password combination exists.
		
		:param username: Email of the user in GraphSpace
		:param password: Password of the user
		:return username: <Username> | None if wrong information
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		# Retrieve hashed password of the user
		cur = con.cursor()
		# TODO: Write query examples
		cur.execute('select password from user where user_id = ?', (username,))

		data = cur.fetchone()

		#If there is no data, then user does not exist
		if data == None:
			return None
		else:
			# If the hash of the passwords are not the same, then the user (theoretically) does not exist
			if bcrypt.hashpw(password, data[0]) != data[0]:
				return None
			else:
				# If everything clears 
				return username

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def get_default_layout(uid, gid):
	'''
		Gets the default layout for a graph.
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		# Retrieve hashed password of the user
		cur = con.cursor()
		# TODO: Write query examples
		cur.execute('select default_layout_id from graph where user_id = ? and graph_id = ?', (uid, gid))
		data = cur.fetchone()

		#If there is no data, then user does not exist
		if data == None:
			return json.dumps(None)
		else:
			cur.execute('select json from layout where layout_id=?', (data[0], ))
			data = cur.fetchone()
			if data != None:
				return json.dumps({"json": cytoscapePresetLayout(json.loads(str(data[0])))})
			else:
				return json.dumps(None)

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return json.dumps(None)
	finally:
		if con:
			con.close()

def get_default_layout_id(uid, gid):
	'''
		Gets the default layout for a graph.
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		# Retrieve hashed password of the user
		cur = con.cursor()
		# TODO: Write query examples
		cur.execute('select default_layout_id from graph where user_id = ? and graph_id = ?', (uid, gid))
		data = cur.fetchone()

		#If there is no data, then user does not exist
		if data == None:
			return None
		else:
			return data[0]

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return json.dumps(None)
	finally:
		if con:
			con.close()

def get_default_layout_name(uid, gid):
	'''
		Gets the default layout for a graph.
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		# Retrieve hashed password of the user
		cur = con.cursor()
		# TODO: Write query examples
		cur.execute('select default_layout_id from graph where user_id = ? and graph_id = ?', (uid, gid))
		data = cur.fetchone()

		#If there is no data, then user does not exist
		if data == None:
			return None
		else:
			cur.execute('select layout_name from layout where layout_id=?', (data[0], ))
			data = cur.fetchone()

			if data == None:
				return None

			return data[0]

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return json.dumps(None)
	finally:
		if con:
			con.close()

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

    # if there is a layout specified, then render that layout
	if len(request.GET.get('layout', '')) > 0:
		if request.GET.get('layout') != 'default_breadthfirst' and request.GET.get('layout') != 'default_concentric' and request.GET.get('layout') != 'default_dagre' and request.GET.get('layout') != 'default_circle' and request.GET.get('layout') != 'default_cose' and request.GET.get('layout') != 'default_cola' and request.GET.get('layout') != 'default_arbor' and request.GET.get('layout') != 'default_springy':
		    temp_uid = None
		    if 'uid' in context:
		    	temp_uid = context['uid']
		    graph_json = get_layout_for_graph(request.GET.get('layout'), gid, uid, temp_uid)
		    if graph_json == None:
		    	context['Error'] = "Layout: " + request.GET.get('layout') + " either does not exist or " + uid + " has not shared this layout yet.  Click <a href='" + URL_PATH + "graphs/" + uid + "/" + gid + "'>here</a> to view this graph without the specified layout."
		    layout_to_view = json.dumps({"json": graph_json})
		    context['default_layout'] = get_default_layout_id(uid, gid)
		else:
			layout_to_view = get_default_layout(uid, gid)
			context['default_layout'] = get_default_layout_id(uid, gid)

		context['layout_name'] = request.GET.get('layout')
	else:
		layout_to_view = get_default_layout(uid, gid)
		context['default_layout'] = get_default_layout_id(uid, gid)
		context['layout_name'] = get_default_layout_name(uid, gid)
		
	context['default_layout_name'] = get_default_layout_name(uid, gid)
	# send layout information to the front-end
	context['layout_to_view'] = layout_to_view
	context['layout_urls'] = URL_PATH + "graphs/" + uid + "/" + gid + "?layout="

	search_type = None

	if 'partial_search' in request.GET:
	    search_type = 'partial_search'
	elif 'full_search' in request.GET:
	    search_type = 'full_search'

	if 'uid' in context:
		context['my_layouts'] = get_my_layouts_for_graph(uid, gid, context['uid'])
		context['shared_layouts'] = list(set(get_shared_layouts_for_graph(uid, gid, context['uid']) + get_public_layouts_for_graph(uid, gid)))
		context['my_shared_layouts'] = get_my_shared_layouts_for_graph(uid, gid, context['uid'])
	else:
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
	con = None
	try:
		con = lite.connect(DB_NAME)

		# Retrieve hashed password of the user
		cur = con.cursor()

		cur.execute('select json, public, graph_id from graph where user_id = ? and graph_id = ?', (uid, gid))
		data = cur.fetchone()

		#If there is no data, then user does not exist
		if data == None:
			return None

		return data

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return json.dumps(None)
	finally:
		if con:
			con.close()

def get_graphs_for_view_type(context, view_type, uid, request):
	'''
		Gets the graphs that are associated with a certain view from the user
		
		:param context: Dictionary containing values to pass to front-end
		:param view_type: Type of view to render
		:param uid: Owner of the graph
		:param request: Get request
		:return context: Dictionary containing values to pass to front-end
	'''

	tag_list = []
	search_list = []

	search_type = None

	if 'partial_search' in request.GET:
		search_type = 'partial_search'
	elif 'full_search' in request.GET:
		search_type = 'full_search'

	search_terms = request.GET.get(search_type)
	tag_terms = request.GET.get('tags') or request.GET.get('tag')
	order_by = request.GET.get('order')
	
	# modify tag information 
	if tag_terms and len(tag_terms) > 0:
		cleaned_tags = tag_terms.split(',')
		client_side_tags = ""
		# Goes through each tag, making it a string
		# so the url will contain those tags as a part
		# of the query string
		for tags in xrange(len(cleaned_tags)):
		    cleaned_tags[tags] = cleaned_tags[tags].strip()
		    if len(cleaned_tags[tags]) == 0:
		    	del cleaned_tags[tags]
		    client_side_tags = client_side_tags + cleaned_tags[tags] + ','

		client_side_tags = client_side_tags[:len(client_side_tags) - 1]
		context['tags'] = client_side_tags
		# This is for the side menu, each tag has its own button
		context['tag_terms'] = cleaned_tags
		tag_list = cleaned_tags

    # modify search information
	if search_terms and len(search_terms) > 0:
		context['search_result'] = True
		cleaned_search_terms = search_terms.split(',')
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

		client_side_search = client_side_search[:len(client_side_search) - 1]
		context['search_word'] = client_side_search
		context['search_type'] = search_type
		context['search_word_terms'] = cleaned_search_terms
		search_list = cleaned_search_terms

	# If there is no one logged in, display only public graph results
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

		# context['graph_list'] = view_graphs(uid, search_type, search_list, tag_list, view_type)
		# context['my_graphs'] = 0#len(view_graphs(uid, search_type, search_list, tag_list, 'my graphs'))
		# context['shared_graphs'] = 0#len(view_graphs(uid, search_type, search_list, tag_list, 'shared'))
		# context['public_graphs'] = 0#len(view_graphs(uid, search_type, search_list, tag_list, 'public'))

	if order_by:
		context['graph_list'] = order_information(order_by, search_terms, context['graph_list'])
	else:
		context['graph_list'] = order_information("modified_descending", search_terms, context['graph_list'])
	return context	

def setDefaultLayout(layoutName, graph_id, graph_owner):
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get all groups that the user owns
		cur.execute('select layout_id from layout where graph_id=? and user_id = ? and layout_name = ? and (unlisted = 1 or public = 1)', (graph_id, graph_owner, layoutName));
		data = cur.fetchone()

		# If there is data, gather all of the tags for this view type and return it
		if data == None or len(data) == 0:
			return "It appears as if the layout either does not exist or is not shared."
		else:
			cur.execute('update graph set default_layout_id = ? where graph_id = ? and user_id = ?', (data[0], graph_id, graph_owner))
			con.commit()
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return "Something went wrong!"

	finally:
		if con:
			con.close()

def removeDefaultLayout(layoutName, graph_id, graph_owner):
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get all groups that the user owns
		cur.execute('select layout_id from layout where graph_id=? and user_id = ? and layout_name = ?', (graph_id, graph_owner, layoutName));
		data = cur.fetchone()

		# If there is data, gather all of the tags for this view type and return it
		if data == None or len(data) == 0:
			return "Layout does not exist for this graph"
		else:
			cur.execute('update graph set default_layout_id = NULL where graph_id = ? and user_id = ?', (graph_id, graph_owner))
			con.commit()
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return "Something went wrong!"

	finally:
		if con:
			con.close()

def order_information(order_term, search_terms, graphs_list):
	'''
		Orders all graph tuples based on order_term.

		:param order_term Term to order by (example, graph, modified, owner)
		:param search_terms Search terms in query (Needed because all search terms add two column (link to graph and node labels) which offsets references by 2)
		:param graph_list Tuples of graphs
		:return sorted_list Sorted list of graph tuples according to order_term
	'''

	if search_terms:
		if order_term == 'graph_ascending':
			return sorted(graphs_list, key=lambda graph: graph[0])
		elif order_term == 'graph_descending':
			return sorted(graphs_list, key=lambda graph: graph[0], reverse=True)
		elif order_term == 'modified_ascending':
			return sorted(graphs_list, key=lambda graph: graph[4])
		elif order_term == 'modified_descending':
			return sorted(graphs_list, key=lambda graph: graph[4], reverse=True)
		elif order_term == 'owner_ascending':
			return sorted(graphs_list, key=lambda graph: graph[5])
		elif order_term == 'owner_descending':
			return sorted(graphs_list, key=lambda graph: graph[5], reverse=True)
		else:
			return graphs_list
	else:
		if order_term == 'graph_ascending':
			return sorted(graphs_list, key=lambda graph: graph[0])
		elif order_term == 'graph_descending':
			return sorted(graphs_list, key=lambda graph: graph[0], reverse=True)
		elif order_term == 'modified_ascending':
			return sorted(graphs_list, key=lambda graph: graph[2])
		elif order_term == 'modified_descending':
			return sorted(graphs_list, key=lambda graph: graph[2], reverse=True)
		elif order_term == 'owner_ascending':
			return sorted(graphs_list, key=lambda graph: graph[3])
		elif order_term == 'owner_descending':
			return sorted(graphs_list, key=lambda graph: graph[3], reverse=True)
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
		search_result_graphs = search_result(uid, search_type, search_terms, view_type)
		
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
		con = None
		try: 
			con = lite.connect(DB_NAME)
			cur = con.cursor()

			# Go through all the tag terms, based on the view type and append them the initial place holder
			for tag in tag_terms:
				if view_type == 'my graphs':
					cur.execute('select g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g, graph_to_tag as gt where gt.graph_id = g.graph_id and gt.tag_id = ? and gt.user_id = ?', (tag, uid))
					
				elif view_type == 'shared':
					cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from group_to_user as gu, graph as g, graph_to_tag as gt, group_to_graph as gg where gg.group_id = gu.group_id and gt.graph_id=g.graph_id and gg.graph_id=g.graph_id and gt.tag_id = ? and gu.user_id=?', (tag, uid))
					
				else:
					cur.execute('select g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g, graph_to_tag as gt where gt.graph_id = g.graph_id and gt.tag_id = ? and g.public = ?', (tag, 1))

				# After the current SQL is executed, collect the results
				data = cur.fetchall()
				for graph in data:
					initial_graphs_with_tags.append(graph)

			# After all the SQL statements have ran for all of the tags, count the number of times
			# a graph appears in the initial list. If it appears as many times as there are 
			# tag terms, then that graph matches all the tag terms and it should be returned
			graph_repititions = defaultdict(int)
			graph_mappings = defaultdict(list)
			# Counting the number of occurences
			for graph_tuple in initial_graphs_with_tags:
				graph_repititions[graph_tuple[0]] += 1

			for graph_tuple in initial_graphs_with_tags:
				graph_list = graph_mappings.get(graph_tuple[0], [])
				graph_list.append(graph_tuple)
				graph_mappings[graph_tuple[0]] = graph_list

			# If value appears the number of times as there are tags, 
			# then append that to the actual list of graphs to be returned.
			actual_graphs_for_tags = []
			for key, value in graph_repititions.iteritems():
				if value == len(tag_terms):
					key_tuples = graph_mappings[key]
					for key_tuple in key_tuples:
						# Insert all tags for the graph in the first index
						key_with_tag = list(key_tuple)
						key_with_tag.insert(1, get_all_tags_for_graph(key_with_tag[0], key_with_tag[2]))
						key_with_tag = tuple(key_with_tag)
						actual_graphs_for_tags.append(key_with_tag)

			return actual_graphs_for_tags

		except lite.Error, e:
			print 'Error %s:' % e.args[0]
			return []
		finally:
			if con:
				con.close()
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

	if search_type != 'partial_search' and search_type !=  'full_search':
		return []

	# Make into list if it is not a lsit
	if not isinstance(search_terms, list):
		search_terms = search_terms.split(',')

	if len(search_terms) > 0:
		intial_graphs_from_search = []
		con = None
		try: 
			con = lite.connect(DB_NAME)
			cur = con.cursor()

			# If it is an edge
			for search_word in search_terms:
				if ':' in search_word:
					intial_graphs_from_search = intial_graphs_from_search + find_edges(uid, search_type, search_word, view_type, cur)
				# If it is a node or possibly a graph_id (name of the graph)
				else:
					intial_graphs_from_search = intial_graphs_from_search + find_nodes(uid, search_type, search_word, view_type, cur) + find_graphs_using_names(uid, search_type, search_word, view_type, cur)
			# intial_graphs_from_search = list(set(intial_graphs_from_search))

			# After all the SQL statements have ran for all of the search_terms, count the number of times
			# a graph appears in the initial list. If it appears as many times as there are 
			# search terms, then that graph matches all the search terms and it should be returned
			graph_repititions = defaultdict(int)
			graph_mappings = defaultdict(list)
			# Counting the number of occurences
			for graph_tuple in intial_graphs_from_search:
				graph_repititions[graph_tuple[0] + graph_tuple[4]] += 1

			for graph_tuple in intial_graphs_from_search:
				graph_list = graph_mappings.get(graph_tuple[0] + graph_tuple[4], [])
				graph_list.append(graph_tuple)
				graph_mappings[graph_tuple[0] + graph_tuple[4]] = graph_list

			# If value appears the number of times as there are tags, 
			# then append that to the actual list of graphs to be returned.
			actual_graphs_for_searches = []
			for key, value in graph_repititions.iteritems():
				if value >= len(search_terms):
					key_tuples = graph_mappings[key]
					ids_and_labels = []
					labels = []
					# Gather all the id's and labels that are part of the same graph 
					# that is being searched for and make them into one tuple
					for key_tuple in key_tuples:
						key_with_search = list(key_tuple)
						ids_and_labels.append(str(key_tuple[1]))
						labels.append(str(key_tuple[2]))
					id_string = ""
					if len(ids_and_labels) > 0:
						for ids in ids_and_labels:
							id_string = id_string + ids + ','

						id_string = id_string[:len(id_string) - 1]

						label_string = ""
						for label in labels:
							label = label.replace('-', ':')
							label_string = label_string + label + ','
						# while label_string[len(label_string) - 1] == ',' or label_string[len(label_string) - 1] == ' ':
						label_string = label_string[:len(label_string) - 1]
						key_with_search = list(key_tuples[0])
						key_with_search.insert(1, "")
						key_with_search[2] = id_string
						key_with_search[3] = label_string
						key_with_search = tuple(key_with_search)
						actual_graphs_for_searches.append(key_with_search)

			# Return whole dictionary of matchin graphs
			return actual_graphs_for_searches

		except lite.Error, e:
			print 'Error %s:' % e.args[0]
			return []
		finally:
			if con:
				con.close()

	else:
		return []

def find_edges(uid, search_type, search_word, view_type, cur):
	'''
		Finds graphs that have the edges that are being searched for.

		:param uid: Owner of the graph
		:param search_type: Type of search (partial_search or full_search)
		:param search_word: Edge being searched for
		:param view_type: Type of view to limit the graphs to
		:param cur: Database cursor
		:return Edges: [Edges]
	'''

	initial_graphs_with_edges = []
	node_ids = search_word.split(':')

	head_node = node_ids[0]
	tail_node = node_ids[1]

	head_node_ids = []
	tail_node_ids = []

	if search_type == 'full_search':
		# treat id's as labels
		cur.execute('select n.node_id from node as n where n.label = ?', (head_node, ))
		head_node_label_data = cur.fetchall()
		head_node_ids = []
		for node in head_node_label_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.label = ?', (tail_node, ))
		tail_node_label_data = cur.fetchall()
		tail_node_ids = []
		for node in tail_node_label_data:
			tail_node_ids.append(str(node[0]))

		# treat id's as node_id's
		cur.execute('select n.node_id from node as n where n.node_id = ?', (head_node, ))
		head_node_id_data = cur.fetchall()
		for node in head_node_id_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.node_id = ?', (tail_node, ))
		tail_node_id_data = cur.fetchall()
		for node in tail_node_id_data:
			tail_node_ids.append(str(node[0]))
	elif search_type == 'partial_search':
		# treat id's as labels
		cur.execute('select n.node_id from node as n where n.label like ?', ('%' + head_node + '%', ))
		head_node_label_data = cur.fetchall()
		head_node_ids = []
		for node in head_node_label_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.label like ?', ('%' + tail_node + '%', ))
		tail_node_label_data = cur.fetchall()
		tail_node_ids = []
		for node in tail_node_label_data:
			tail_node_ids.append(str(node[0]))

		# treat id's as node_id's
		cur.execute('select n.node_id from node as n where n.node_id like ?', ('%' + head_node + '%', ))
		head_node_id_data = cur.fetchall()
		for node in head_node_id_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.node_id like ?', ('%' + tail_node + '%', ))
		tail_node_id_data = cur.fetchall()
		for node in tail_node_id_data:
			tail_node_ids.append(str(node[0]))

	head_node_ids = list(set(head_node_ids))
	tail_node_ids = list(set(tail_node_ids))

	# If there are any graphs that fit the criteria, 
	# return the graphs that are under the type of graphs
	# that the user wants to see (his/her graphs, or public etc)
	if len(head_node_ids) > 0 and len(tail_node_ids) > 0:
		for i in xrange(len(head_node_ids)):
			for j in xrange(len(tail_node_ids)):
				if view_type == 'public':
					cur.execute('select e.head_graph_id, e.head_id, e.label, datetime(g.modified), e.head_user_id, g.public from edge as e, graph as g where e.head_id = ? and e.tail_id = ? and e.head_graph_id = g.graph_id and g.public = 1', (head_node_ids[i], tail_node_ids[j]))
				elif view_type == 'shared':
					cur.execute('select e.head_graph_id, e.head_id, e.label, datetime(g.modified), e.head_user_id, g.public from edge as e, graph as g, group_to_graph as gg where gg.user_id = ? and e.head_graph_id = gg.graph_id and e.head_id = ? and e.tail_id = ? and e.head_graph_id = g.graph_id', (uid, head_node_ids[i], tail_node_ids[j]))
				else:
					cur.execute('select e.head_graph_id, e.head_id, e.label, datetime(g.modified), e.head_user_id, g.public from edge as e, graph as g where e.head_user_id = ? and e.head_graph_id = g.graph_id and e.head_id = ? and e.tail_id = ?', (uid, head_node_ids[i], tail_node_ids[j]))

				data = cur.fetchall()
				initial_graphs_with_edges = add_unique_to_list(initial_graphs_with_edges, data)
				
	actual_graph_with_edges = []
	for graph in initial_graphs_with_edges:
		graph_list = list(graph)
		# Appending the nodes that are being searched for
		graph_list[1] = graph_list[2] + ' (' + head_node + '-' + tail_node + ')'
		actual_graph_with_edges.append(tuple(graph_list))

	return actual_graph_with_edges


def uploadCyjsFile(username, graphJSON, title):
	parseJson = {"graph": {"edges": [], "nodes": []}, "metadata": {}}

	csjs = json.loads(graphJSON)

	if 'elements' not in csjs:
		return {"Error": "No elements property inside of file!"}

	if 'nodes' not in csjs['elements']:
		return {"Error": "File must contain nodes property in elements dictionary!"}

	if 'edges' not in csjs['elements']:
		return {"Error": "File must contain edges property in elements dictionary!"}

	for node in csjs['elements']['nodes']:
		tempNode = {"data": {}}
		tempNode['data']['id'] = node['data']['id']
		if 'node_fillColor' in node['data'] and len(node['data']['node_fillColor']) > 0:
			# tempNode['data']['background_color'] = rgb_to_hex(node['data']['node_fillColor'])
			tempNode['data']['background_color'] = node['data']['node_fillColor']
		tempNode['data']['content'] = node['data']['name']
		tempNode['data']['shape'] = "ellipse"
		parseJson['graph']['nodes'].append(tempNode)

	for edge in csjs['elements']['edges']:
		tempEdge = {"data": {}}
		tempEdge['data']['source'] = edge['data']['source']
		tempEdge['data']['target'] = edge['data']['target']
		tempEdge['data']['popup'] = edge['data']['name']
		parseJson['graph']['edges'].append(tempEdge)

	parseJson['metadata']['name'] = csjs['data']['name']
	parseJson['metadata']['tags'] = []
	parseJson['metadata']['description'] = ""

	title = title or parseJson['metadata']['name']

	if username != None:
		result = insert_graph(username, title, json.dumps(parseJson))
		if result == None:
			return {"Success": URL_PATH + "graphs/" + username + "/" + title}
		else:
			return {"Error": result}
	else:
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

def uploadJSONFile(username, graphJSON, title):


	parseJson = json.loads(graphJSON)

	if 'metadata' not in parseJson:
		parseJson['metadata'] = {}

	if 'name' not in parseJson['metadata']:
		parseJson['metadata']['name'] = "graph_" + str(datetime.now())

	title = title or parseJson['metadata']['name']

	if username != None:
		result = insert_graph(username, title, json.dumps(parseJson))
		if result == None:
			return {"Success": URL_PATH + "graphs/" + username + "/" + title}
		else:
			return {"Error": result}
	else:
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

def delete_30_day_old_anon_graphs():
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute("delete FROM graph where user_id like '%Public_User_%' and created >= date('now','-30 day')");
		con.commit()

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return e.args[0]
	finally:
		if con:
			con.close()


def rgb_to_hex(rgb):
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
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('insert into user values(?,?,?,?,?,?,?)', (public_user_id, 'test', 1, 1, 1, 1, 0))
		con.commit()
		return None
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return e.args[0]
	finally:
		if con:
			con.close()

def delete_public_user():
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('delete into user where user=?', ("test", ))
		con.commit()
		return None
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return e.args[0]
	finally:
		if con:
			con.close()


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
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		head_node = edge_to_find.split(':')[0]
		tail_node = edge_to_find.split(':')[1]

		if search_type == 'partial_search':

			# Find node id's that are being searched for (source and target nodes)
			head_nodes = find_node(uid, gid, head_node, 'partial_search')
			tail_nodes = find_node(uid, gid, tail_node, 'partial_search')

			edge_list = []
			if len(head_node) > 0 and len(tail_node) > 0:
				for i in xrange(len(tail_nodes)):
					for j in xrange(len(head_nodes)):
						cur.execute('select label from edge where tail_id = ? and head_id = ? and head_user_id = ? and head_graph_id = ? limit 1', (tail_nodes[i], head_nodes[j], uid, gid))
						data = cur.fetchall()
						if data and len(data) > 0:
							edge_list.append(data[0])

				return edge_list
		else:
			# Find node id's that are being searched for (source and target nodes)
			head_node = find_node(uid, gid, head_node, 'full_search')
			tail_node = find_node(uid, gid, tail_node, 'full_search')

			# If both nodes exist, find label between them
			if tail_node != None and head_node != None and len(tail_node) > 0 and len(head_node) > 0:
				cur.execute('select label from edge where tail_id = ? and head_id = ? and head_user_id = ? and head_graph_id = ? limit 1', (str(tail_node[0]), str(head_node[0]), uid, gid))
				data = cur.fetchall()
				# If something exists, return the ids of the paents
				if data != None and len(data) > 0:
					return data[0]
				else:
					return []
	
		return []

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return []
	finally:
		if con:
			con.close()

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

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		if search_type == 'partial_search':
			# Get the id of the node (could be id or a label) and return it if they exist
			cur.execute('select node_id from node where node_id LIKE ? and user_id = ? and graph_id = ?', ('%' + node_to_find + '%', uid, gid))
			id_data = cur.fetchall()
			id_list = []

			for ids in id_data:
				id_list.append(str(ids[0]))
	
			cur.execute('select node_id from node where label LIKE ? and user_id = ? and graph_id = ?', ('%' + node_to_find + '%', uid, gid))
			label_data = cur.fetchall()
			for labels in label_data:
				id_list.append(str(labels[0]))
			
			id_list = list(set(id_list))

			if len(id_list) > 0:
				return id_list

		elif search_type == 'full_search':
			# Get the id of the node (could be id or a label) and return it if they exist
			cur.execute('select node_id from node where node_id = ? and user_id = ? and graph_id = ? limit 1', (node_to_find, uid, gid))
			id_data = cur.fetchall()
			if id_data != None and len(id_data) > 0:
				return [id_data[0][0]]
			else:
				cur.execute('select node_id from node where label = ? and user_id = ? and graph_id = ? limit 1', (node_to_find, uid, gid))
				label_data = cur.fetchall()

				if label_data != None and len(label_data) > 0:
					return [label_data[0][0]]

		return []

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return []
	finally:
		if con:
			con.close()

def intersect(a, b):
     return list(set(a) & set(b))

def find_nodes(uid, search_type, search_word, view_type, cur):
	'''
		Finds graphs that have the nodes that are being searched for.

		:param uid: Owner of the graph
		:param search_type: partial or full matching
		:param search_word: Node being searched for
		:param view_type: Type of view to limit the graphs to
		:param cur: Database cursor
		:return Nodes: [Nodes]
	'''
	intial_graph_with_nodes = []

	if search_type == 'partial_search':
		if view_type == 'my graphs':
			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.label LIKE ? and n.user_id = ?', ('%' + search_word + '%', uid))
			node_labels = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, node_labels)

			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.node_id LIKE ? and n.user_id = ?', ('%' + search_word + '%', uid))
			node_ids = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, node_ids)
		elif view_type == 'shared':
			before = datetime.now().second

			cur.execute('select group_id, group_owner from group_to_user where user_id= ? and group_owner <> ?', (uid, uid))
			groups_user_belongs_to = cur.fetchall()

			graphs_in_group = []
			for single_group in groups_user_belongs_to:
				cur.execute('select graph_id, user_id from group_to_graph where group_id = ? and group_owner = ?', (single_group[0], single_group[1]))
				graphs_in_group += cur.fetchall()

			graphs_in_group = list(set(graphs_in_group))
			
			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.label LIKE ? and n.user_id <> ?', ('%' + search_word + '%', uid))
			node_info = cur.fetchall()
			node_info = list(set(node_info))

			final_graphs = []

			for matched in node_info:
				searched_graph = (matched[0], matched[4])
				if searched_graph in graphs_in_group:
					final_graphs.append(matched)

			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, final_graphs)

			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.node_id LIKE ? and n.user_id <> ?', ('%' + search_word + '%', uid))
			node_info = cur.fetchall()
			node_info = list(set(node_info))

			final_graphs = []

			for matched in node_info:
				searched_graph = (matched[0], matched[4])
				if searched_graph in graphs_in_group:
					final_graphs.append(matched)

			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, final_graphs)
			after = datetime.now().second

		else:
			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.label LIKE ? and n.public = 1', ('%' + search_word + '%', ))
			public_labels = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, public_labels)

			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.node_id LIKE ? and n.public = 1', ('%' + search_word + '%', ))
			public_ids = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, public_ids)

	elif search_type == 'full_search':
		if view_type == 'my graphs':
			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.label = ? and n.user_id = ?', (search_word, uid))
			node_labels = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, node_labels)

			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.node_id = ? and n.user_id = ?', (search_word, uid))
			node_ids = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, node_ids)
		
		elif view_type == 'shared':
			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n, group_to_graph as gg, group_to_user as gu where n.label = ? and gg.graph_id = n.graph_id and n.user_id = gg.user_id and gu.user_id = ? and gg.group_owner <> ? and gu.group_id = gg.group_id and gu.group_owner = gg.group_owner', (search_word, uid, uid))
			shared_labels = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, shared_labels)

			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n, group_to_graph as gg, group_to_user as gu where n.node_id = ? and gg.graph_id = n.graph_id and n.user_id = gg.user_id and gu.user_id = ? and gg.group_owner <> ? and gu.group_id = gg.group_id and gu.group_owner = gg.group_owner', (search_word, uid, uid))
			shared_ids = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, shared_ids)

		else:
			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.label = ? and n.public = 1', ( search_word, ))
			public_labels = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, public_labels)

			cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, n.modified, n.user_id, n.public from node as n where n.node_id = ? and n.public = 1', ( search_word, ))
			public_ids = cur.fetchall()
			intial_graph_with_nodes = add_unique_to_list(intial_graph_with_nodes, public_ids)

	return intial_graph_with_nodes

def find_graphs_using_names(uid, search_type, search_word, view_type, cur):
	'''	
		Finds graphs that have the matching graph name.

		:param uid: Owner of the graph
		:param search_type: Type of search (full_search or partial_search)
		:param search_word: Graph names being searched for
		:param view_type: Type of view to limit the graphs to
		:param cur: Database cursor
		:return Graphs: [Graphs]
	'''

	if search_type == 'partial_search':
		if view_type == 'my graphs':
			cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where g.graph_id LIKE ? and g.user_id= ?', ('%' + search_word + '%', uid))
		elif view_type == 'shared':
			cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g, group_to_graph as gg, group_to_user as gu where g.graph_id LIKE ? and gu.user_id= ? and gu.group_id = gg.group_id and g.graph_id = gg.graph_id', ('%' + search_word + '%', uid))
		else:
			cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where g.graph_id LIKE ? and g.public= 1', ('%' + search_word + '%', ))

	elif search_type == 'full_search':
		if view_type == 'my graphs':
			cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where g.graph_id = ? and g.user_id= ?', (search_word, uid))
		elif view_type == 'shared':
			cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g, group_to_graph as gg, group_to_user as gu where g.graph_id = ? and gu.user_id= ? and gu.group_id = gg.group_id and g.graph_id = gg.graph_id', (search_word, uid))
		else:
			cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where g.graph_id = ? and g.public= 1', (search_word, ))

	graph_list = cur.fetchall()

	return graph_list

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

def insert_graph(username, graphname, graph_json, created=None, modified=None, public=0, unlisted=1, default_layout_id=None, skip=None):
	'''
		# TODO: Add rest call example
		Inserts a uniquely named graph under a username.

		:param username: Email of user in GraphSpace
		:param graphname: Name of graph to insert
		:param graph_json: JSON of graph
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		# TODO: Write query examples
		# Checks to see if a user already has a graph with the same name under his account
		cur.execute('select graph_id from graph where user_id = ? and graph_id = ?', (username, graphname))

		data = cur.fetchone()

		# If not, add this graph to his account
		if data == None:
			if skip != True:
				validationErrors = validate_json(graph_json)
				if validationErrors != None:
					return validationErrors

			curTime = datetime.now()
			graphJson = json.loads(graph_json)

			# Checks to see if it is compatible with CytoscapeJS and converts it accordingly
			# TODO: Delete this after Verifier is finished
			if 'data' in graphJson['graph']:
				graphJson = json.loads(convert_json(graph_json))

			# Attach ID's to each edge for traversing the element
			graphJson = assign_edge_ids(graphJson)

			# Go through all the nodes in the JSON and if they don't have a label,
			# Append a random label to it
			# Used so that I can highlight the node
			# TODO: double check this because I may need to get the id and not the label
			nodes = graphJson['graph']['nodes']
			# rand = 1
			# for node in nodes:
			# 	if 'data' in node and 'content' in node['data'] and len(node['data']['content']) == 0:
			# 		node['data']['content'] = rand
			# 		rand = rand + 1
			rand = 0

			# Inserts it into the database, all graphs inserted are private for now
			# TODO: Verify if that is what I want
			if modified == None and created == None:
				cur.execute('insert into graph values(?, ?, ?, ?, ?, ?, ?, ?)', (graphname, username, json.dumps(graphJson, sort_keys=True, indent=4), curTime, curTime, public, unlisted,default_layout_id))
			elif modified == None:
				cur.execute('insert into graph values(?, ?, ?, ?, ?, ?, ?, ?)', (graphname, username, json.dumps(graphJson, sort_keys=True, indent=4), created, curTime, public, unlisted,default_layout_id))
			elif created == None:
				cur.execute('insert into graph values(?, ?, ?, ?, ?, ?, ?, ?)', (graphname, username, json.dumps(graphJson, sort_keys=True, indent=4), curTime, modified, public, unlisted,default_layout_id))
			else:
				cur.execute('insert into graph values(?, ?, ?, ?, ?, ?, ?, ?)', (graphname, username, json.dumps(graphJson, sort_keys=True, indent=4), created, modified, public, unlisted,default_layout_id))
			
			if 'tags' in graphJson['metadata']:
				tags = graphJson['metadata']['tags']
			else:
				tags = []

			# Insert all tags for this graph into tags database
			insert_data_for_graph(graphJson, graphname, username, tags, nodes, cur, con, curTime, 0)
			# Commit the changes
			con.commit()

			# If everything works, return Nothing 
			return None
	
		else:
			return 'Graph ' + graphname + ' already exists for ' + username + '!'

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return e.args[0]

	finally:
		if con:
			con.close()

def insert_data_for_graph(graphJson, graphname, username, tags, nodes, cur, con, modified, public):
	'''
		Inserts metadata about a graph into its respective tables.

		:param graphJson: JSON of graph
		:param graphname: Name of graph
		:username: Name of user
		:param: Tags of graph
		:param Nodes: Nodes to insert into nodes table
		:param cur: Database cursor
		:param con: Database connection
	'''
	
	# Add all tags for this graph into graph_tag and graph_to_tag tables
	for tag in tags:
		# TODO: Query example
		cur.execute('select tag_id from graph_tag where tag_id=?', (tag, ))
		tagData = cur.fetchone()
		if tagData == None:
			cur.execute('insert into graph_tag values(?)', (tag, ))

		cur.execute('insert into graph_to_tag values(?,?,?)', (graphname, username, tag))

	edges = graphJson['graph']['edges']

	dupEdges = []

	rand = 0
	# Add all edges and nodes in the JSON to their respective tables
	for edge in edges:
		if 'target_arrow_shape' not in edge['data']:
			edge['data']['target_arrow_shape'] = "none"

		if edge['data']['source'] + '-' + edge['data']['target'] in dupEdges:
			rand += 1
			cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge['data']["source"] + str(rand), graphname, graphname, edge['data']["target"] + str(rand), edge['data']['id'], 1))
			dupEdges.append(edge['data']['source'] + str(rand) + '-' + edge['data']['target'] + str(rand))
		else:
			cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge['data']["source"], graphname, graphname, edge['data']["target"], edge['data']['id'], 1))
		# if (edge['data']['source'] in dupEdges):
		# 	rand += 1
		# 	if 'target_arrow_shape' in edge['data']:
		# 		cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge['data']["source"] + str(rand), graphname, graphname, edge['data']["target"], edge['data']['id'], 1))
		# 	else:
		# 		cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge['data']["source"] + str(rand), graphname, graphname, edge['data']["target"], edge['data']['id'], 1))
		# 	dupEdges.append(edge['data']['source']);
		# else:
		# 	if 'target_arrow_shape' in edge['data']:
		# 		cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge['data']["source"], graphname, graphname, edge['data']["target"], edge['data']['id'], 1))
		# 	else:
		# 		cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge['data']["source"], graphname, graphname, edge['data']["target"], edge['data']['id'], 1))
		
		# 	dupEdges.append(edge['data']['source']);
	for node in nodes:
		cur.execute('insert into node values(?,?,?,?,?,?)', (node['data']['id'], node['data']['content'], username, graphname, modified, public))

def update_graph(username, graphname, graph_json):
	'''
		Updates the JSON for a graph.
	
		:param username: Email of user in GraphSpace
		:param graphname: Name of graph to insert
		:param graph_json: JSON of graph
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select graph_id, public, unlisted, default_layout_id from graph where user_id = ? and graph_id = ?', (username, graphname))
		data = cur.fetchone()

		if data != None:

			public = data[1]
			unlisted = data[2]
			default_layout = str(data[3])

			result = insert_graph(username, graphname, graph_json)
			if result != None:

				cur.execute('select * from graph where user_id = ? and graph_id = ?', (username, graphname))
				old_graph = cur.fetchone()
				# Deletes information about a graph from all the tables that reference it
				cur.execute('delete from graph where user_id = ? and graph_id = ?', (username, graphname))
				cur.execute('delete from graph_to_tag where graph_id=? and user_id=?', (graphname, username))
				cur.execute('delete from edge where head_graph_id =? and head_user_id=?', (graphname, username))
				cur.execute('delete from node where graph_id = ? and user_id=?', (graphname, username))
				con.commit()
				result = insert_graph(username, graphname, graph_json, old_graph[3], datetime.now(), public,unlisted,default_layout)
				if result == None:
					return result
				else:
					insert_graph(username, graphname, old_graph[2], old_graph[3], old_graph[4], old_graph[5], old_graph[6], old_graph[7])
					return result
			else:
				return result
		else:
			return "Can't update " + graphname + " because it does not exist for " + username

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()


def get_graph_json(username, graphname):
	'''
		Get the JSON of the graph to view.

		:param username: Email of user in GraphSpace
		:param password: Password of the user
		:return JSON: JSON of graph to view
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Return the JSON of the graph that matches the username and the graphname
		cur.execute('select json from graph where user_id = ? and graph_id = ?', (username, graphname))

		jsonData = cur.fetchone()

		# If there is JSON for this graph, return it
		if jsonData and jsonData[0]:
			return jsonData[0]
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def delete_graph(username, graphname):
	'''
		Deletes graph from database.

		:param username: Email of user in GraphSpace
		:param password: Password of the user
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Deletes information about a graph from all the tables that reference it
		cur.execute('delete from graph where user_id = ? and graph_id = ?', (username, graphname))
		cur.execute('delete from graph_to_tag where graph_id=? and user_id=?', (graphname, username))
		cur.execute('delete from edge where head_graph_id =? and head_user_id=?', (graphname, username))
		cur.execute('delete from group_to_graph where graph_id =? and user_id=?', (graphname, username))
		cur.execute('delete from node where graph_id = ? and user_id=?', (graphname, username))
		cur.execute('delete from layout where graph_id = ? and user_id=?', (graphname, username))
		con.commit()

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def get_all_graphs_for_user(username):
	'''
		Gets all graphs for username

		:param username: Email of user in GraphSpace
		:return Graphs: [graphs]
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Query for all graphs by a specific user
		cur.execute('select graph_id from graph where user_id = ?', (username, ))

		data = cur.fetchall()

		# If there are graphs for the user, return them 
		if data != None:
			cleaned_data = []
			for graphs in data:
				cleaned_data.append(str(graphs[0]))

			if len(cleaned_data) > 0:
				return cleaned_data

		return []

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def get_all_groups_in_server():
	'''
		Gets all groups that are in the server
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Group is written this way because SQLITE wouldn't accept it simply as group
		cur.execute('select group_id, group_name, owner_id, public from \"group\"');

		data = cur.fetchall()

		if data == None:
			return None

		cleaned_data = []

		# Return information about the group
		for group in data:
			cleaned_record = {"owner": group[2], "id": group[0], "description": group[3]}
			cleaned_data.append(cleaned_record)

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_groups_of_user(user_id):
	'''
		Get all groups that the user owns

		:param user_id: Email of user of GraphSpace
		:return Groups: [group information]
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get all groups that the user owns
		cur.execute('select * from \"group\" where owner_id=?', (user_id, ))

		data = cur.fetchall()

		# Clean up the data
		return get_cleaned_group_data(data, cur)
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_cleaned_group_data(data, cur):
	'''
		Get all information about group (including number of graphs group has)

		:param data: Information about group
		:param cur: Database cursor
		:return Groups: [gorup information + graphs in group information]
	'''

	cleaned_data = []

	# Go through and create an index including the number of graphs that a group has 
	for group_name in data:
		cleaned_group = []
		cleaned_group.append(group_name[1])
		cleaned_group.append(group_name[3])
		cleaned_group.append(group_name[2])
		cur.execute('select count(*) from group_to_graph where group_id=? and group_owner=?', (group_name[0], group_name[2]))
		new_data = cur.fetchall()
		cleaned_group.append(new_data[0][0])
		cleaned_group.append(group_name[4])
		cleaned_group.append(group_name[5])
		cleaned_group.append(group_name[0])
		cleaned_group = tuple(cleaned_group)

		cleaned_data.append(cleaned_group)

	return cleaned_data

def get_all_groups_with_member(user_id):
	'''
		Get all groups that has the user as a member in that group.

		:param user_id: Member to be searched for in all groups
		:return Groups: [Groups that user_id is a member of]
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()

		# Get all groups that user is a member of
		cur.execute('select group_id, group_owner from group_to_user where user_id=?', (user_id, ))

		group_names = cur.fetchall()

		# Get information about those groups
		cleaned_data = []
		for group_name in group_names:
			cur.execute('select * from \"group\" where group_id=? and owner_id=?', (group_name[0], group_name[1]))
			data = cur.fetchall()
			cleaned_data += get_cleaned_group_data(data, cur)

		return list(set(cleaned_data))

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def change_description(username, groupId, groupOwner, desc):
	'''
		Changes description of group.

		:param username: person who is requesting the change
		:param groupId: ID of group to change description 
		:param groupOwner: Owner of the group
		:param desc: Description to change to
		:return Error: <error>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()

		if username != groupOwner:
			return "You can only change description of group that you own!"

		cur.execute('update "group" set description = ? where owner_id = ? and group_id = ?', (desc, groupOwner, groupId))
		con.commit()

		return None
		
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return e.args[0]

	finally:
		if con:
			con.close()
def get_group_by_id(groupOwner, groupId):
	'''
		Gets a group information by group id ( REST API option).
		
		:param groupOwner: Owner of the group
		:param groupId: ID of group to be searched for
		:return Group: [Information about group (see REST API in Help section)]
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		# Get information about group
		cur = con.cursor()
		cur.execute('select description, owner_id, name, group_id from \"group\" where owner_id = ? and group_id=?', (groupOwner, groupId));

		data = cur.fetchall()

		cleaned_data = []

		# Remove group owner's name from member's list to display in UI
		initial_members = get_group_members(groupOwner, groupId)
		members = []

		for member in initial_members:
			if member != groupOwner:
				members.append(member)

		# Get members of the group 
		for row in data:
			tuple_list = (str(row[0]), members, str(row[1]), str(row[2]), str(row[3]))
			cleaned_data.append(tuple_list)

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_group(group_owner, groupId):
	'''
		Gets all information about a certain group (used for groups page exclusively).
        
        :param group_owner: Owner of group to get from server
		:param groupId: ID of groupId
		:return Group: [information of group]
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		cur.execute('select description, owner_id, name, group_id from \"group\" where group_id=? and owner_id=?', (groupId, group_owner));

		data = cur.fetchall()

		if len(data) == 0:
			return None

		cleaned_data = {}
		# Get group members and graphs in group etc
		for row in data:
			cleaned_data['members'] = get_group_members(group_owner, groupId)
			cleaned_data['owner'] = str(row[1])
			cleaned_data['group_id'] = str(row[3])
			cleaned_data['description'] = str(row[0])
			cur.execute('select graph_id from group_to_graph where group_id=? and group_owner = ?', (groupId, group_owner))
			cleaned_data['graphs'] = []
			graph_data = cur.fetchall()
			if len(graph_data) > 0:
				for graph in graph_data:
					cleaned_data['graphs'].append(graph[0])

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()


def get_group_members(groupOwner, groupId):
	'''
		Get all members of a group.

		:param groupOwner: Group Owner 
		:param groupId: Group ID
		:return Members: [Members of group]
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		cur.execute('select user_id from group_to_user where group_owner = ? and group_id=?', (groupOwner, groupId));

		data = cur.fetchall()

		# Get all members and clean up the data
		cleaned_data = []
		for member in data:
			cleaned_data.append(str(member[0]))

		# If user is owner of the group, they can also see the graph!
		cur.execute('select owner_id from "group" where owner_id = ? and group_id=?', (groupOwner, groupId));
		data = cur.fetchall()

		for owner in data:
			cleaned_data.append(str(owner[0]))

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def can_see_shared_graph(logged_in_user, graph_owner, graphname):
	'''
		See if user is allowed to see a graph.

		:param logged_in_user: User that is currently logged in
		:param graph_owner: Owner of graph being viewed
		:param graphname: Name of graph being viewed
		:return boolean: True if can see it, false otherwise
	'''

	groups = get_all_groups_for_this_graph(graph_owner, graphname)
	if len(groups) > 0:
		for group in groups:
			members = get_group_members(group[1], group[0])
	        if logged_in_user in members:
	            return True

	return None

def remove_group(owner, group):
	'''
		Removes a group from server.

		:param owner: Owner of group
		:param group: Group ID
		:return <result
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# If there is a group with this owner, then remove it from the server
		cur.execute('select owner_id from \"group\" where owner_id=? and group_id=?', (owner, group, ));

		data = cur.fetchone()
		if data == None:
			return "Group not found!"

		if data[0] == None:
			return "Can't remove group"
		else:
			# Remove metadata from tables
			cur.execute('delete from \"group\" where owner_id=? and group_id=?', (owner, group, ))
			cur.execute('delete from group_to_graph where group_owner=? and group_id=?', (owner, group))
			cur.execute('delete from group_to_user where group_owner = ? and group_id=?', (owner, group))
			con.commit();
			return "Successfully deleted " + group + " owned by " + owner + "."

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def create_group(username, group):
	'''
		Inserts a uniquely named group under a username.

		:param owner: Owner of group
		:param group: Group ID
		:return <result>
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Check to see if there is a group under the username already 
		cur.execute('select group_id from \"group\" where group_id=? and owner_id=?', (group, username));
		data = cur.fetchone()

		# If no group exists, insert into database
		if data == None:
			cur.execute('insert into \"group\" values(?, ?, ?, ?, ?, ?)', (cleanGroupName(group), group, username, "", 0, 1))
			con.commit()
			return [group, cleanGroupName(group)]
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

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
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		#TODO: add what a user can see as well (ie has access to)
		# Get groups that the user is a member of
		cur.execute('select group_id, group_owner from group_to_user where user_id=?', (username, ))

		data = cur.fetchall()

		cleaned_data=[]
		for groups in data:
			groups = {"groupId": str(groups[0]), "group_owner": str(groups[1])}
			cleaned_data.append(groups)

		# Get all the groups that the user owns as well
		cur.execute('select group_id from \"group\" where owner_id=?', (username, ))

		data = cur.fetchall()

		for groups in data:
			groups = {"groupId": str(groups[0]), "group_owner": username}
			cleaned_data.append(groups)

		return cleaned_data

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()


def find_edges_for_graphs_in_group(groupOwner, groupId, search_type, word, cur):
	initial_graphs_with_edges = []
	node_ids = word.split(':')

	head_node = node_ids[0]
	tail_node = node_ids[1]

	head_node_ids = []
	tail_node_ids = []

	if search_type == 'full_search':
		# treat id's as labels
		cur.execute('select n.node_id from node as n where n.label = ?', (head_node, ))
		head_node_label_data = cur.fetchall()
		head_node_ids = []
		for node in head_node_label_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.label = ?', (tail_node, ))
		tail_node_label_data = cur.fetchall()
		tail_node_ids = []
		for node in tail_node_label_data:
			tail_node_ids.append(str(node[0]))

		# treat id's as node_id's
		cur.execute('select n.node_id from node as n where n.node_id = ?', (head_node, ))
		head_node_id_data = cur.fetchall()
		for node in head_node_id_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.node_id = ?', (tail_node, ))
		tail_node_id_data = cur.fetchall()
		for node in tail_node_id_data:
			tail_node_ids.append(str(node[0]))
	elif search_type == 'partial_search':
		# treat id's as labels
		cur.execute('select n.node_id from node as n where n.label LIKE ?', ('%' + head_node + '%', ))
		head_node_label_data = cur.fetchall()
		head_node_ids = []
		for node in head_node_label_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.label LIKE ?', ('%' + tail_node + '%', ))
		tail_node_label_data = cur.fetchall()
		tail_node_ids = []
		for node in tail_node_label_data:
			tail_node_ids.append(str(node[0]))

		# treat id's as node_id's
		cur.execute('select n.node_id from node as n where n.node_id LIKE ?', ('%' + head_node + '%', ))
		head_node_id_data = cur.fetchall()
		for node in head_node_id_data:
			head_node_ids.append(str(node[0]))

		cur.execute('select n.node_id from node as n where n.node_id LIKE ?', ('%' + tail_node + '%', ))
		tail_node_id_data = cur.fetchall()
		for node in tail_node_id_data:
			tail_node_ids.append(str(node[0]))

	head_node_ids = list(set(head_node_ids))
	tail_node_ids = list(set(tail_node_ids))


	# If there are any graphs that fit the criteria, 
	# return the graphs that are under the type of graphs
	# that the user wants to see (his/her graphs, or public etc)
	if len(head_node_ids) > 0 and len(tail_node_ids) > 0:
		for i in xrange(len(head_node_ids)):
			for j in xrange(len(tail_node_ids)):
				cur.execute('select e.head_graph_id, e.head_id, e.label, datetime(g.modified) e.head_user_id, g.public from edge as e, graph as g, group_to_graph as gg where e.head_graph_id = gg.graph_id and e.head_id = ? and e.tail_id = ? and e.head_graph_id = g.graph_id and group_id = ? and gg.group_owner = ?', (head_node_ids[i], tail_node_ids[j], groupId, groupOwner))

				data = cur.fetchall()
				initial_graphs_with_edges = add_unique_to_list(initial_graphs_with_edges, data)
				
	actual_graph_with_edges = []
	for graph in initial_graphs_with_edges:
		graph_list = list(graph)
		# Appending the nodes that are being searched for
		graph_list[1] = graph_list[2] + ' (' + head_node + '-' + tail_node + ')'
		actual_graph_with_edges.append(tuple(graph_list))

	return actual_graph_with_edges


def find_nodes_for_graphs_in_group(groupOwner, groupId, search_type, word, cur):
	labels_and_id_matched_graphs = []

	if search_type == 'partial_search':

		cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, datetime(n.modified), n.user_id, n.public from node as n, group_to_graph as gg where n.label Like ? and gg.graph_id = n.graph_id and gg.user_id = n.user_id and gg.group_id = ? and gg.group_owner = ?', ('%' + word + '%', groupId, groupOwner))
		labels_and_id_matched_graphs = add_unique_to_list(labels_and_id_matched_graphs, cur.fetchall())

		cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, datetime(n.modified), n.user_id, n.public from node as n, group_to_graph as gg where n.node_id Like ? and gg.graph_id = n.graph_id and gg.user_id = n.user_id and gg.group_id = ? and gg.group_owner = ?', ('%' + word + '%', groupId, groupOwner))
		labels_and_id_matched_graphs = add_unique_to_list(labels_and_id_matched_graphs, cur.fetchall())

	elif search_type == 'full_search':
		cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, datetime(n.modified), n.user_id, n.public from node as n, group_to_graph as gg where n.label = ? and gg.graph_id = n.graph_id and gg.user_id = n.user_id and gg.group_id = ? and gg.group_owner = ?', (word, groupId, groupOwner))
		labels_and_id_matched_graphs = add_unique_to_list(labels_and_id_matched_graphs, cur.fetchall())

		cur.execute('select n.graph_id, n.node_id || " (" || n.label || ")", n.label, datetime(n.modified), n.user_id, n.public from node as n, group_to_graph as gg where n.node_id = ? and gg.graph_id = n.graph_id and gg.user_id = n.user_id and gg.group_id = ? and gg.group_owner = ?', (word, groupId, groupOwner))
		labels_and_id_matched_graphs = add_unique_to_list(labels_and_id_matched_graphs, cur.fetchall())
	
	# actual_graph_with_nodes = []
	# for graph in labels_and_id_matched_graphs:
	# 	graph_list = list(graph)
	# 	graph_list[1] = graph_list[1] + ' (' + graph_list[2] + ')'
	# 	actual_graph_with_nodes.append(tuple(graph_list))

	return labels_and_id_matched_graphs

def find_graphs_for_group_using_names(uid, groupOwner, groupId, search_type, word, cur):
	intial_graph_names = []

	if search_type == 'partial_search':
		cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g, group_to_graph as gg where g.graph_id LIKE ? and g.graph_id = gg.graph_id and g.user_id = gg.user_id and gg.group_id = ? and gg.group_owner = ?', ('%' + word + '%', groupId, groupOwner))
	elif search_type == 'full_search':
		cur.execute('select g.graph_id, "" as placeholder, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g, group_to_graph as gg where g.graph_id = ? and g.user_id = gg.user_id and g.graph_id = gg.graph_id and gg.group_id = ? and gg.group_owner = ?', (word, groupId, groupOwner))

	intial_graph_names = add_unique_to_list(intial_graph_names, cur.fetchall())
	
	return intial_graph_names

def search_result_for_graphs_in_group(uid, groupOwner, groupId, search_type, search_terms, cur):
	
	intial_graphs_from_search = []

	for word in search_terms:
		if ':' in word:
			intial_graphs_from_search += find_edges_for_graphs_in_group(groupOwner, groupId, search_type, word, cur)
		else:
			intial_graphs_from_search += find_nodes_for_graphs_in_group(groupOwner, groupId, search_type, word, cur) + find_graphs_for_group_using_names(uid, groupOwner, groupId, search_type, word, cur)

	# After all the SQL statements have ran for all of the search_terms, count the number of times
	# a graph appears in the initial list. If it appears as many times as there are 
	# search terms, then that graph matches all the tag terms and it should be returned
	graph_repititions = defaultdict(int)
	graph_mappings = defaultdict(list)
	# Counting the number of occurences
	for graph_tuple in intial_graphs_from_search:
		graph_repititions[graph_tuple[0] + graph_tuple[4]] += 1

	for graph_tuple in intial_graphs_from_search:
		graph_list = graph_mappings.get(graph_tuple[0] + graph_tuple[4], [])
		graph_list.append(graph_tuple)
		graph_mappings[graph_tuple[0] + graph_tuple[4]] = graph_list

	# If value appears the number of times as there are tags, 
	# then append that to the actual list of graphs to be returned.
	actual_graphs_for_searches = []
	for key, value in graph_repititions.iteritems():
		if value >= len(search_terms):
			key_tuples = graph_mappings[key]
			ids_and_labels = []
			labels = []

			# Gather all the id's and labels that are part of the same graph 
			# that is being searched for and make them into one tuple
			for key_tuple in key_tuples:
				key_with_search = list(key_tuple)
				ids_and_labels.append(str(key_tuple[1]))
				labels.append(str(key_tuple[2]))
			id_string = ""
			if len(ids_and_labels) > 0:
				for ids in ids_and_labels:
					id_string = id_string + ids.strip() + ','

				id_string = id_string[:len(id_string) - 1]
				label_string = ""
				for label in labels:
					label = label.replace('-', ':')
					label_string = label_string + label.strip() + ','

				label_string = label_string[:len(label_string) - 1]
				key_with_search = list(key_tuples[0])
				key_with_search.insert(1, "")
				key_with_search[2] = id_string
				key_with_search[3] = label_string
				key_with_search = tuple(key_with_search)
				actual_graphs_for_searches.append(key_with_search)

	# Return whole dictionary of matchin graphs
	return actual_graphs_for_searches

def tag_result_for_graphs_in_group(groupOwner, groupId, tag_terms, cur):

	initial_graphs_with_tags = []

	for tag in tag_terms:
		cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from group_to_user as gu, graph as g, graph_to_tag as gt, group_to_graph as gg where gg.group_id = ? and gg.group_owner = ? and gg.graph_id = gt.graph_id and gt.tag_id = ? and gt.graph_id = g.graph_id and gt.user_id = g.user_id', (groupId, groupOwner, tag))
		initial_graphs_with_tags += cur.fetchall()

	# After all the SQL statements have ran for all of the tags, count the number of times
	# a graph appears in the initial list. If it appears as many times as there are 
	# tag terms, then that graph matches all the tag terms and it should be returned
	graph_repititions = defaultdict(int)
	graph_mappings = defaultdict(list)
	# Counting the number of occurences
	for graph_tuple in initial_graphs_with_tags:
		graph_repititions[graph_tuple[0]] += 1

	for graph_tuple in initial_graphs_with_tags:
		graph_list = graph_mappings.get(graph_tuple[0], [])
		graph_list.append(graph_tuple)
		graph_mappings[graph_tuple[0]] = graph_list

	# If value appears the number of times as there are tags, 
	# then append that to the actual list of graphs to be returned.
	actual_graphs_for_tags = []
	for key, value in graph_repititions.iteritems():
		if value == len(tag_terms):
			key_tuples = graph_mappings[key]
			for key_tuple in key_tuples:
				# Insert all tags for the graph in the first index
				key_with_tag = list(key_tuple)
				key_with_tag.insert(1, get_all_tags_for_graph(key_with_tag[0], key_with_tag[2]))
				key_with_tag = tuple(key_with_tag)
				actual_graphs_for_tags.append(key_with_tag)

	return actual_graphs_for_tags

def get_all_graphs_for_group(uid, groupOwner, groupId, request):
	'''
		Get all graphs that belong to this group.

		:param groupOwner: Owner of group
		:param groupId: Id of group
		:param search_terms: Terms to be searched for
		:param tag_terms: Tags to be searched for in graphs
		:return Graphs: [graphs]
	'''
	con = None

	search_type = None

	if 'partial_search' in request.GET:
		search_type = 'partial_search'
	elif 'full_search' in request.GET:
		search_type = 'full_search'

	search_terms = request.GET.get(search_type)
	tag_terms = request.GET.get('tags') or request.GET.get('tag')
	order_by = request.GET.get('order')

	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		if search_terms and tag_terms:
			return []

		elif search_terms:
			graph_data = search_result_for_graphs_in_group(uid, groupOwner, groupId, search_type, search_terms.split(','), cur)

		elif tag_terms:
			graph_data = tag_result_for_graphs_in_group(groupOwner, groupId, tag_terms.split(','), cur)

		else:
			cur.execute('select g.graph_id, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where exists ( select * from group_to_graph as gg where gg.group_owner= ? and g.user_id = gg.user_id and gg.group_id = ? and gg.graph_id = g.graph_id)', (groupOwner, groupId))
			graph_data = cur.fetchall()

		if order_by:
			graph_data = order_information(order_by, search_terms, graph_data)
		else:
			graph_data = order_information("modified_descending", search_terms, graph_data)

		return graph_data

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_all_groups_for_user_with_sharing_info(graphowner, graphname):
	'''
		Gets all groups that a user owns or is a member of,
		and indicates whether the specified graph is shared with that group

		:param owner: Owner of graph
		:param grpahname: Name of graph
		:return group_info: [{group_name: <name of group>, "graph_shared": boolean}]
	'''
	group_info = []
	groups = get_groups_of_user(graphowner) + get_all_groups_with_member(graphowner)
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# For all groups user is a part of, indicate whether specified graph is shared with that group
		for group in groups:
			cur.execute('select * from group_to_graph where group_id = ? and group_owner=? and user_id = ? and graph_id = ?', (group[6], group[2], graphowner, graphname))
			is_shared = cur.fetchone()

			if is_shared == None:
				group_info.append({"group_name": group[0], "group_owner": group[2], "group_id": group[6], "graph_shared": False})
			else:
				group_info.append({"group_name": group[0], "group_owner": group[2], "group_id": group[6], "graph_shared": True})

		return group_info

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

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
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select user_id from user where user_id=?', (username, ))

		data = cur.fetchone()
		if data == None:
			return "User does not exist!"

		# If user exists and the owner of the group is issuing the request, then add the user to the group
		cur.execute('select group_id from group_to_user where user_id=? and group_id=?', (owner, group, ))
		isMember = cur.fetchone()

		cur.execute('select owner_id from \"group\" where owner_id=? and group_id=?', (owner, group))
		isOwner = cur.fetchone()

		if isMember != None or isOwner != None:
			cur.execute('insert into group_to_user values(?, ?, ?)', (group, owner, username))
			con.commit();
			return "Successfully added user " + username + " to " + group + "."
		else:
			return "Become the owner/member of this group first!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def remove_user_from_group(username, owner, group):
	'''
		Removes user from group.

		:param username: User to remove
		:param owner: Owner of group
		:param group: Group ID
		:return <status>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select user_id from user where user_id=?', (username, ))
		data = cur.fetchone()


		if data == None:
			return "User does not exist!"

		# If user exists and they are owner of the group, delete the requested username from the group
		data = data[0]
		cur.execute('select owner_id from \"group\" where owner_id=? and group_id=?', (owner, group, ))
		isOwner = cur.fetchone()
		if isOwner != None:
			isOwner = isOwner[0]
			cur.execute('delete from group_to_user where user_id=? and group_id=? and group_owner = ?', (username, group, owner))
			cur.execute('delete from group_to_graph where user_id=? and group_id=? and group_owner = ?', (username, group, owner))
			con.commit();
			return "Successfully removed user " + username + " from " + group + "."
		else:
			return "Can't delete user from a group you are not the owner of!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def remove_user_through_ui(username, owner, group):
	'''
		Removes user from group through UI.

		:param username: User to remove
		:param owner: Owner of group
		:param group: Group ID
		:return <status>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select user_id from user where user_id=?', (username, ))
		data = cur.fetchone()

		if data == None:
			return "User does not exist!"

		cur.execute('delete from group_to_user where user_id=? and group_id=? and group_owner=?', (username, group, owner))
		cur.execute('delete from group_to_graph where user_id=? and group_id=? and group_owner = ?', (username, group, owner))
		con.commit();
		return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def share_graph_with_group(owner, graph, groupId, groupOwner):
	'''
		Shares a graph with group.
		
		:param owner: Owner of group
		:param graph: Graph to share 
		:param groupId: Group ID
		:param groupOwner: Group Owner
		:return <status>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get graph information ** MUST ALREADY EXIST IN GRAPHSPACE **
		cur.execute('select * from graph where user_id=? and graph_id=?', (owner, graph))
		data = cur.fetchone()
		if data == None:
			return 'Graph does not exist'

		isOwner = data[0]

		# If there is a graph for the owner, then we add that graph to the group that a user is a part of (user or member)
		if isOwner != None:
			cur.execute('select user_id from group_to_user where user_id=? and group_id=? and group_owner=?', (owner, groupId, groupOwner))
			isMember = cur.fetchone()
			cur.execute('select owner_id from \"group\" where owner_id = ? and group_id = ?', (groupOwner, groupId))
			isOwner = cur.fetchone()
			# If the query returns, it means that the owner is a member of that group
			if isMember != None or isOwner != None:
				cur.execute('insert into group_to_graph values(?, ?, ?, ?)', (groupId, groupOwner, owner, graph))
				con.commit()
				return None
			else:
				return "You are not a member of this group!"
		else:
			return "You don't own this graph!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def unshare_graph_with_group(owner, graph, groupId, groupOwner):
	'''
		Graph to unshare with group.

		:param owner: Owner of group
		:param graph: Graph to unshare 
		:param groupId: Group ID
		:param groupOwner: Group Owner
		:return <status>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get the graph that the user supposedly owns
		cur.execute('select user_id from graph where user_id=? and graph_id=?', (owner, graph, ))
		graph_owner = cur.fetchone()
		cur.execute('select user_id from group_to_graph where graph_id=? and user_id=? and group_id=? and group_owner = ?', (graph, owner, groupId, groupOwner))
		graph_in_group = cur.fetchone()
		if graph_owner != None and graph_in_group != None:
			cur.execute('delete from group_to_graph where group_id=? and group_owner=? and graph_id=? and user_id=?', (groupId, groupOwner, graph, owner))
			con.commit()
			return None
		else:
			return "You don't own this graph or graph isn't shared with the group yet!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()


# ---------------- END REST API ------------------------------

def view_graphs_of_type(view_type, username):
	'''
		View graphs of this type e.g. shared, my graphs, public.

		:param view_type: Type of view (shared, public)
		:param username: Name of user
		:return Graphs: [graphs]
	'''
	graphs = []
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Select graphs depending on view type.
		if view_type == 'public':
			cur.execute('select distinct g.graph_id, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where g.public = 1')
		elif view_type == 'shared':
			cur.execute('select distinct g.graph_id, "" as placeholder, datetime(g.modified), g.user_id, g.public from group_to_graph as gg, group_to_user as gu, graph as g where g.graph_id = gg.graph_id and gu.user_id=? and gu.group_id = gg.group_id', (username, ))
		else:
			cur.execute('select distinct g.graph_id, "" as placeholder, datetime(g.modified), g.user_id, g.public from graph as g where g.user_id = ?', (username, ))

		# Go through each graph and retrieve all tags associated with that graph
		graphs = cur.fetchall()
		
		# Return the graph information (including tags) as a list of rows
		return graphs

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return []

	finally:
		if con:
			con.close()

def get_graphs_for_tags(cur, username, tags):
	'''
		Returns graphs that match the tags.

		:param cur: Database cursor
		:param username: Name of User
		:param tags: tags to match graphs to
		:return Graphs: [graphs]
	'''
	graphs = []
	all_tag_graphs = get_all_graphs_for_tags(tags)
	for item in all_tag_graphs:
		cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from group_to_user as gu, graph as g, graph_to_tag as gt, group_to_graph as gg where gg.group_id = gu.group_id and gt.graph_id=g.graph_id and gg.graph_id=g.graph_id and gt.tag_id = ? and gu.user_id=?', (item, username))
		data = cur.fetchall()
		if data != None:
			for thing in data:
				if thing[0] in all_tag_graphs and thing not in graphs:
					graphs.append(thing)

	return graphs

def get_graph_info(username, tags):
	'''
		Gets graph information about a graph that the user owns having certain tags.

		:param username: Email of user
		:param tags: Tags of graph to filter
		:return Graph: [graph information]
	'''

	graphs = []
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		if tags:
			all_tag_graphs = get_all_graphs_for_tags(tags)
			for item in all_tag_graphs:
				cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g, graph_to_tag as gt where g.graph_id=gt.graph_id and g.user_id=? and gt.graph_id=?', (username, item))
				data = cur.fetchall()
				if data != None:
					for thing in data:
						if thing[0] in all_tag_graphs and thing not in graphs:
							graphs.append(thing)
		else:
			cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g where g.user_id=?', (username, ))
			graphs = cur.fetchall()

		if graphs == None:
			return None
		
		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))

			graph_list = list(graph)
			if len(cleanedtags) > 0:
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))
			else:
				graph_list.insert(1, "")
				cleaned_graph.append(tuple(graph_list))

		if cleaned_graph != None:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_public_graph_info(tags):
	'''
		Get all public graphs that contain the following tags.

		:param tags: Tags to match the graphs to
		:return Graphs: [graphs with tags]
	'''

	con = None
	graphs = []
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		if tags:
			all_tag_graphs = get_all_graphs_for_tags(tags)

			for item in all_tag_graphs:
				cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g where g.public = ? and g.graph_id=?', (1, item))
				data = cur.fetchall()
				if data != None:
					for thing in data:
						if thing[0] in all_tag_graphs and thing not in graphs:
							graphs.append(thing)
		else:
			cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g where g.public=?', (1, ))
			graphs = cur.fetchall()

		if graphs == None:
			return None
		
		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))


			if len(cleanedtags) > 0:
				# for tag in tags:
				graph_list = list(graph)
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))

		if len(cleaned_graph) > 0:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_all_graph_info(tags):
	'''
		Gets all the information about a graph that user owns that matches the tags.

		:param tags: Tags that the user owns
		:return Graphs: [graphs with tags]
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		cur.execute('select distinct g.graph_id, datetime(g.modified), g.user_id, g.public from graph as g')
		graphs = cur.fetchall()
		if graphs == None:
			return None
		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))


			if len(cleanedtags) > 0:
				# for tag in tags:
				graph_list = list(graph)
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))

		if cleaned_graph != None:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def is_public_graph(username, graph):
	'''
		Checks to see if a given graph for a user is public.

		:param username: Email of user
		:param graph: Graph of user
		:return boolean: True if public graph
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# If there is a graph with the username and graph, return if it is public or not
		cur.execute('select public from graph where user_id=? and graph_id=?', (username, graph))
		public = cur.fetchone()

		if public == None:
			return None

		public = public[0]
		
		if public == 1:
			return True
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_all_groups_for_this_graph(uid, graph):
	'''
		Gets all the groups that the graph is shared with.

		:param uid: User of the graph
		:param graph: Name of graph
		:return Groups: [groups]
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select group_id, group_owner from group_to_graph where graph_id=? and user_id=?', (graph, uid))
		graphs = cur.fetchall()

		if graphs == None:
			return None
		
		cleaned_graphs = []
		if graphs != None:
			for graph in graphs:
				cleaned_graphs.append((str(graph[0]), str(graph[1])))
			
			return cleaned_graphs
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def change_graph_visibility(isPublic, user_id, graphName):
	'''
		Makes specified graph and all associated layouts public or private

		:param isPublic boolean that decides if graph is made public or private (0 if private, 1 if public)
		:param user_id ID of owner of graph
		:param graphName name of graph to make public
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select graph_id from graph where user_id = ? and graph_id = ?', (user_id, graphName))

		if len(cur.fetchall()) == 0:
			return "Graph with name " + graphName + " doesn't exist under " + user_id + '.'

		cur.execute('update graph set public = ? where user_id = ? and graph_id = ?', (isPublic, user_id, graphName))
		cur.execute('update layout set public = ? where user_id = ? and graph_id = ? and unlisted = 1', (isPublic, user_id, graphName))
		con.commit()

	except lite.Error, e:
		return 'Error %s:' % e.args[0]
		return e.args[0]

	finally:
		if con:
			con.close()

def is_layout_shared(layoutId, layoutOwner, uid, graphName):
	'''
		Returns if a specified layout is shared

		:param layoutId ID of layout
		:param layoutOwner owner of layout
		:param uid person requesting if layout is shared
		:param graphName graph that layout is associated with
		:return boolean True if layout is shared with uid
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		graph_groups = get_all_groups_for_this_graph(uid, graphName)
		user_groups = get_groups_of_user(layoutOwner) + get_all_groups_with_member(layoutOwner)

		layout_groups = []

		for graph in graph_groups:
			for user_graph in user_groups:
				sub_graph_info = (str(user_graph[6]), str(user_graph[2]))
				if graph == sub_graph_info:
					cur.execute('select layout_id from layout where layout_id=? and owner_id=? and graph_id=? and user_id=?', (layoutId, layoutOwner, graph[1], uid))
					data = cur.fetchone()
					sub_graph_info = list(sub_graph_info)
					if data != None and len(data) > 0:
						sub_graph_info.append(True)
					else:
						sub_graph_info.append(False)

					sub_graph_info = tuple(sub_graph_info)

					layout_groups.append(sub_graph_info)

		if is_public_graph(uid, graphName):
			layout_groups.append(("Public", "GraphSpace"))

		return layout_groups
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def emailExists(email):
	'''
		Checks to see if a user's email exists.

		:param email: Email of user
		:return boolean: True if user exists
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		cur.execute("select * from user where user_id = ?", [email])

		if cur.rowcount == 0:
			return None

		data = cur.fetchone()
		return data

	except lite.Error, e:
   
    		print "Error %s:" % e.args[0]

	finally:
		if con:
			con.close()

def sendForgotEmail(email):
	'''
		Emails the user to reset their password.

		:param email of user
	'''

	if emailExists(email) != None:
		con=None
		try:
			con = lite.connect(DB_NAME)
			cur = con.cursor()

			cur.execute("select code from password_reset where user_id = ?", [email])

			if cur.rowcount == 0:
				return None

			data = cur.fetchall()
			if len(data) == 0:
				return "Email does not exist!"

			mail_title = 'Password Reset Information for GraphSpace!'
			message = 'Please go to the following url to reset your password: ' + URL_PATH + 'reset/?id=' + str(data[0][0])
			emailFrom = "GraphSpace Admin"
			send_mail(mail_title, message, emailFrom, [email], fail_silently=True)
			return "Email Sent!"
		except lite.Error, e:
			print "Error %s: " %e.args[0]

		finally:
			if con:
				con.close()
	else:
		return None

def retrieveResetInfo(code):
	'''
		Retrieves the reset information for a user (for comparing which user it is).

		:param code: Code that the user has to match to HTTP GET request
		:return account: Account associated with the code 
	'''

	con=None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		cur.execute("select user_id from password_reset where code = ?", (code, ))

		if cur.rowcount == 0:
			return None

		data = cur.fetchone()

		if data == None:
			return None

		accountToReset = data[0]
		return accountToReset
	except lite.Error, e:
		print "Error %s: " %e.args[0]

	finally:
		if con:
			con.close()

def resetPassword(username, password):
	'''
		Updates password information about a user.

		:param username: Email of user
		:param password: Password of user

	'''

	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute("update user set password = ? where user_id = ?", (bcrypt.hashpw(password, bcrypt.gensalt()), username))
		cur.execute('delete from password_reset where user_id=?', (username, ))

		con.commit();
		return "Password Updated!"
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

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

	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('update layout set layout_name = ? where owner_id=? and graph_id = ? and layout_name = ? ', (new_layout_name, uid, gid, old_layout_name))
		con.commit()

	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

# Makes a layout public
def makeLayoutPublic(uid, gid, public_layout):
	'''
		Makes a layout public.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param public_layout: Name of layout
	'''
	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select public from layout where owner_id=? and graph_id = ? and layout_name = ? ', (uid, gid, public_layout))
		data = cur.fetchone()

		isPublic = data[0]

		if isPublic == 0:
			cur.execute('update layout set public = 1 where owner_id=? and graph_id = ? and layout_name = ? ', (uid, gid, public_layout))
		else:
			cur.execute('update layout set public = 0 where owner_id=? and graph_id = ? and layout_name = ? ', (uid, gid, public_layout))
		con.commit()

	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()
# Saves layout of a specified graph
def save_layout(layout_id, layout_name, owner, graph, user, json, public, unlisted):
	'''
		Saves layout of specific graph.

		:param layout_id: Id of layout to save
		:param layout_name: Name of layout to save
		:param owner: Owner of the graph
		:param graph: Name of the graph
		:param user: user making those changes
		:param json: JSON of the graph
		:param public: Is layout public or not
		:param unlisted: Possible deprecated
	'''
	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select layout_id from layout where layout_name = ? and owner_id = ? and graph_id = ?', (layout_name, owner, graph))
		layoutExists = cur.fetchall()

		if len(layoutExists) > 0:
			return "Layout with this name already exists for this graph! Please choose another name."	

		cur.execute("insert into layout values(?,?,?,?,?,?,?,?)", (None, layout_name, owner, graph, user, json, 0, 0))
		con.commit()
		return None
	except lite.Error, e:
		print "Error %s: " % e.args[0]
		return e.args[0]
	finally:
		if con:
			con.close()

def deleteLayout(uid, gid, layoutToDelete, loggedIn):
	'''
		Deletes layout from graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param layoutToDelete: name of layout to delete
		:param loggedIn: User that is deleting the graph
	'''
	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()
		
		cur.execute('select layout_id from layout where layout_name = ? and owner_id = ? and graph_id = ?' , (layoutToDelete, uid, gid))
		data = cur.fetchone()

		if data:
			cur.execute('select default_layout_id from graph where graph_id = ? and user_id = ?', (gid, uid))
			layout_id = cur.fetchone()

			if layout_id != None and layout_id[0] == data[0]:
				cur.execute('update graph set default_layout_id = NULL where graph_id = ? and user_id = ?', (gid, uid))
				con.commit()

		cur.execute('delete from layout where layout_name = ? and owner_id = ? and graph_id = ?' , (layoutToDelete, uid, gid))
		con.commit()

		return None
	except lite.Error, e:
		print "Error %s: " % e.args[0]
		return e.args[0]
	finally:
		if con:
			con.close()


def get_layout_for_graph(layout_name, graph_id, graph_owner, loggedIn):
	'''
		Retrieves specific layout for a certain graph.

		:param layout_name: Name of layout
		:param layout_graph: Name of graph
		:param layout_owner: Owner of layout
		:param loggedIn: Logged in user
		:return Layout: [layout]
	'''
	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get JSON of layout
		# cur.execute("select json, unlisted, public, user_id from layout where layout_name =? and graph_id=? and owner_id=? and user_id=?", (layout_name, graph_id, graph_owner, loggedIn))
		cur.execute("select json, unlisted, public, user_id from layout where layout_name =? and graph_id=? and owner_id=?", (layout_name, graph_id, graph_owner))
		data = cur.fetchone()

		if data == None:
			return None

		if loggedIn != data[3]:
			if data[1] == 0 and data[2] == 0:
				return None

		return cytoscapePresetLayout(json.loads(str(data[0])))

	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

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
	con=None
	try:
		con = lite.connect(DB_NAME)

		cur = con.cursor()
		cur.execute("select layout_name from layout where owner_id =? and graph_id=?", (uid, gid))
		
		data = cur.fetchall()

		if data == None:
			return None

		cleaned_data = []
		for graphs in data:
			graphs = str(graphs[0])
			cleaned_data.append(graphs)

		return cleaned_data
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()


def share_layout_with_all_groups_of_user(owner, gid, layoutId):
	'''
		Shares a layout with all the groups that owner of a graph is a part of.
		
		:param uid: Owner of graph
		:param gid: Name of graph
		:param layoutId: LayoutID of the graph
	'''

	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()
		
		cur.execute('select unlisted from layout where owner_id=? and graph_id = ? and layout_name = ? ', (owner, gid, layoutId))
		data = cur.fetchone()

		isListed = data[0]

		if isListed == 0:
			cur.execute('update layout set unlisted = 1 where layout_name = ? and owner_id = ? and graph_id = ?', (layoutId, owner, gid))
		else:
			cur.execute('update layout set unlisted = 0 where layout_name = ? and owner_id = ? and graph_id = ?', (layoutId, owner, gid))
			cur.execute('update graph set default_layout_id=NULL where graph_id = ? and user_id = ?', (gid, owner))

		con.commit()
		
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

# Gets my layouts for a graph
def get_my_layouts_for_graph(uid, gid, loggedIn):
	'''
		Get my layouts for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param loggedIn: Current user of graphspace
		:return Layouts: [my layouts of graph]
	'''
	con=None
	try:
		con = lite.connect(DB_NAME)

		# Get my layouts
		cur = con.cursor()
		cur.execute("select layout_name from layout where owner_id =? and graph_id=? and user_id=? and unlisted = 0 and public=0", (uid, gid, loggedIn))
		
		data = cur.fetchall()

		if data == None:
			return None

		cleaned_data = []
		for graphs in data:
			graphs = str(graphs[0])
			cleaned_data.append(graphs)

		return cleaned_data
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

def get_shared_layouts_for_graph(uid, gid, loggedIn):
	'''
		Get shared layouts for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param loggedIn: Current user of graphspace
		:return Layouts: [shared layouts of graph]
	'''
	# # Get all shared groups for this graph
	# all_groups_for_graph = get_all_groups_for_this_graph(uid, gid)
	# shared_graphs = []
	# # Get all members of the shared groups
	# for group in all_groups_for_graph:
	# 	members = get_group_members(group[0], group[1])
	# 	if loggedIn in members:
	# 		for member in members:
	# 			if loggedIn != member:
	# 				shared_graphs += get_my_layouts_for_graph(uid, gid, member)

	# return shared_graphs

	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		all_groups_for_graph = get_all_groups_for_this_graph(uid, gid)

		for group in all_groups_for_graph:
			members = get_group_members(group[1], group[0])
			if loggedIn in members:
				cur.execute("select layout_name from layout where owner_id =? and graph_id=? and unlisted=1", (uid, gid))
				data = cur.fetchall()

				if data == None:
					return []

				cleaned_data = []
				for layouts in data:
					layouts = str(layouts[0])
					cleaned_data.append(layouts)

				return cleaned_data

		return []
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return []
	finally:
		if con:
			con.close()

def get_my_shared_layouts_for_graph(uid, gid, loggedIn):
	'''
		Get shared layouts of the graph owner for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:param loggedIn: Current user of graphspace
		:return Layouts: [shared layouts of graph]
	'''
	# # Get all shared groups for this graph
	# all_groups_for_graph = get_all_groups_for_this_graph(uid, gid)
	# shared_graphs = []
	# # Get all members of the shared groups
	# for group in all_groups_for_graph:
	# 	members = get_group_members(group[0], group[1])
	# 	if loggedIn in members:
	# 		for member in members:
	# 			if loggedIn != member:
	# 				shared_graphs += get_my_layouts_for_graph(uid, gid, member)

	# return shared_graphs

	con=None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute("select distinct layout_name from layout where owner_id =? and graph_id=? and user_id=? and (unlisted = 1 or public = 1)", (uid, gid, loggedIn))
		
		data = cur.fetchall()

		if data == None:
			return []

		cleaned_data = []

		for layouts in data:
			layouts = str(layouts[0])
			cleaned_data.append(layouts)
		
		return cleaned_data
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return []
	finally:
		if con:
			con.close()

# def share_layout_with_group(layoutId, layoutOwner, graphId, groupId, groupOwner):

# 	con=None
# 	try:
# 		con = lite.connect(DB_NAME)

# 		# Get my layouts
# 		cur = con.cursor()

# 		cur.execute('insert into layout values(?, ?,?,?,?)', (layoutOwner, ))

# 	except lite.Error, e:
# 		print "Error %s: " %e.args[0]
# 		return None
# 	finally:
# 		if con:
# 			con.close()
			
def get_public_layouts_for_graph(uid, gid):
	'''
		Get public layouts for this graph.

		:param uid: Owner of graph
		:param gid: Name of graph
		:return Layouts: [public layouts of graph]
	'''
	con=None
	try:
		con = lite.connect(DB_NAME)

		# Get public layouts
		cur = con.cursor()
		cur.execute("select layout_name from layout where owner_id =? and graph_id=? and public=1", (uid, gid))
		
		data = cur.fetchall()

		if data == None:
			return []

		# Replace any spaces with html equivalent
		cleaned_data = []
		for graphs in data:
			graphs = str(graphs[0])
			cleaned_data.append(graphs)

		return cleaned_data
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return []
	finally:
		if con:
			con.close()

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

		con=None
		try:
			con = lite.connect(DB_NAME)
			cur = con.cursor()

			graphs_for_tag_list = []
			actual_graphs_for_tags = []
			# Search for graphs for each tag term and append them to list
			for tag_id in tag_terms:
				cur.execute('select distinct g.graph_id from graph as g, graph_to_tag as gt where gt.tag_id=? and g.graph_id = gt.graph_id', (tag_id, ))
				data = cur.fetchall()
				if data != None:
					for item in data:
						graphs_for_tag_list.append(item[0])

			# Get number of times the graph names appear.
			# If they appear the same number of times as the lenght of the tag terms
			# it implicitly means that the graph has all of the tags that are being searched for.
			# Those graphs that pass the length check are returned as having all of the tags
			accurate_tags = Counter(graphs_for_tag_list)
			for graph in graphs_for_tag_list:
				if accurate_tags[graph] == len(tag_terms):
					actual_graphs_for_tags.append(graph)

			return actual_graphs_for_tags

		except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
		finally:
			if con:
				con.close()
	else:
		return None

# find all tags for a user
def get_all_tags_for_user(username):
	'''
		Return all tags that a user has for their graphs.

		:param username: Email of user in GraphSpace
		:return Tags: [tags]
	'''

	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		# Get tags that the user has and return them
		tags_list = []
		cur.execute('select distinct tag_id from graph_to_tag where user_id = ?', (username, ))
		data = cur.fetchall()
		if data != None:
			for item in data:
				tags_list.append(item[0])

		return tags_list

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

def get_all_tags_for_graph(graphname, username):
	'''
		Returns all of the tags for a specific graph.
	
		:param graphname: Name of graph to search for
		:param username: Email of user in GraphSpace
		:return Tags: [tags of graph]
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		tags_list = []

		# Get all tags for specified graph and return it
		cur.execute('select distinct tag_id from graph_to_tag where user_id = ? and graph_id=?', (username, graphname))
		data = cur.fetchall()

		if data != None:
			for item in data:
				tags_list.append(str(item[0]))

		return tags_list

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

def change_graph_visibility_for_tag(isPublic, tagname, username):
	'''
		Makes all graphs under a tag owned by username public.

		:param isPublic: If graphs are to be made public (0 for private, 1 for public)
		:param tagname: Name of tag to search for
		:param username: Email of user in GraphSpace
		:return <Message>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		graph_list = []

		cur.execute('select user_id from graph_to_tag where tag_id = ? and user_id = ?', (tagname, username))
		data = cur.fetchall()

		if len(data) == 0:
			return "No graphs exist for " + username + " for tag: " + tagname + '.'

		# Get all tags for specified graph and return it
		cur.execute('update graph set public = ? where user_id in (select user_id from graph_to_tag where tag_id=? and user_id=?) and graph_id in (select graph_id from graph_to_tag where tag_id=? and user_id=?)', (isPublic, tagname, username, tagname, username))
		cur.execute('update node set public = ? where user_id in (select user_id from graph_to_tag where tag_id=? and user_id=?) and graph_id in (select graph_id from graph_to_tag where tag_id=? and user_id=?)', (isPublic, tagname, username, tagname, username))
		cur.execute('update layout set public = ? where owner_id = ? and user_id in (select user_id from graph_to_tag where tag_id=? and user_id=?) and graph_id in (select graph_id from graph_to_tag where tag_id=? and user_id=?)', (username, isPublic, tagname, username, tagname, username))

		con.commit()

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

def delete_all_graphs_for_tag(tagname, username):
	'''
		Deletes all graphs under a tag owned by username.

		:param tagname: Name of tag to search for
		:param username: Email of user in GraphSpace
		:return <Message>
	'''
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		graph_list = []

		# Get all tags for specified graph and return it
		cur.execute('delete from graph where graph_id = (select graph_id from graph_to_tag where tag_id=? and user_id=?) and user_id = (select user_id from graph_to_tag where tag_id=? and user_id=?)', (tagname, username, tagname, username))
		cur.execute('delete from graph_to_tag where tag_id=? and user_id=?', (tagname, username))

		con.commit()
		return "Done"

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

def getGraphInfo(uid, gid):
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select json, public, graph_id from graph where user_id = ? and graph_id = ?', (uid, gid))
		data = cur.fetchone()

		if data == None:
			return None
		else:
			return data

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

def retrieveJSON(uid, gid):
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('select json from graph where user_id = ? and graph_id = ?', (uid, gid))
		data = cur.fetchone()

		if data == None:
			return None
		else:
			return data

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

def insert_user(user_id, password, activated, activate_code, public, unlisted, admin):
	con = None
	try:
		con = lite.connect(DB_NAME)
		cur = con.cursor()

		cur.execute('insert into user values (?,?,?,?,?,?,?)', (user_id, password, activated, activate_code, public, unlisted, admin))
		con.commit()

	except lite.Error, e:
			print "Error %s: " %e.args[0]
			return None
	finally:
		if con:
			con.close()

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
