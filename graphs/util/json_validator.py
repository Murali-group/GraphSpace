## See http://js.cytoscape.org/#style/node-body
ALLOWED_NODE_SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle', 
                       'pentagon', 'hexagon', 'heptagon', 'octagon', 'star', 
                       'diamond', 'vee', 'rhomboid']

ALLOWED_NODE_BORDER_STYLES = ['solid', 'dotted', 'dashed','double']

ALLOWED_NODE_BACKGROUND_REPEAT = ['no-repeat', 'repeat-x', 'repeat-y', 'repeat']

ALLOWED_NODE_TEXT_TRANSFORM = ['none', 'uppercase', 'lowercase']

ALLOWED_NODE_TEXT_WRAP = ['none', 'wrap']

ALLOWED_TEXT_BACKROUND_SHAPE = ['rectangle', 'roundrectangle']

ALLOWED_TEXT_HALIGN = ['left', 'center', 'right']

ALLOWED_TEXT_VALIGN = ['top', 'center', 'bottom']

## See http://js.cytoscape.org/#style/labels
ALLOWED_TEXT_WRAP = ['wrap','none']

## See http://js.cytoscape.org/#style/edge-arrow
ALLOWED_ARROW_SHAPES = ['tee', 'triangle', 'triangle-tee', 'triangle-backcurve', 
                        'square', 'circle', 'diamond', 'none']

## See http://js.cytoscape.org/#style/edge-line
ALLOWED_EDGE_STYLES = ['solid', 'dotted','dashed']

ALLOWED_ARROW_FILL = ['filled', 'hollow']

import json

def verify_json(graph_json):
    graph_json = json.loads(graph_json)

    for node in graph_json["graph"]["nodes"]:
        node = node["data"]

        if "shape" in node:
            shape = node["shape"].lower()
        else:
            shape = "ellipse"

        if shape not in ALLOWED_NODE_SHAPES:
            shape = "ellipse"

        node["shape"] = shape
    
    return json.dumps(graph_json)

def validate_json(graphJson):
    """
    Validates JSON to see if all properties are consistent with API.

    @param graphJson: JSON of graph
    """

    cleaned_json = json.loads(graphJson)

    if 'data' in cleaned_json:
        cleaned_json = convert_json(cleaned_json)

    if "graph" not in cleaned_json:
        return "JSON of graph must have 'graph' property"

	if "nodes" not in cleaned_json["graph"]:
		return "JSON of graph must have 'nodes' property"

	if isinstance(cleaned_json["graph"]["nodes"], list) == False:
		return "Nodes property must contain an array"

    if "edges" not in cleaned_json["graph"]:
		return "JSON of graph must have 'edges' property"

    if isinstance(cleaned_json["graph"]["edges"], list) == False:
		return "Edges property must contain an array"

    # Validate all node properties
    error = validate_node_properties(cleaned_json["graph"]["nodes"])

    if error != None:
        return error

    # Validate all edge properties
    error = validate_edge_properties(cleaned_json["graph"]["edges"])

    if error != None:
        return error

def validate_edge_properties(edges):
    """
    Validates all edge properties.

    @param edges: Array of edge objects (http://js.cytoscape.org)
    """

    error = ""
    edge_id = None
    # Go through all edges to verify if edges contain valid properties
    # recognized by CytoscapeJS
    for edge in edges:
        edge = edge["data"]

    	# If edge has no source and target nodes, throw error since they are required
    	if "source" not in edge or "target" not in edge:
    		return "All edges must have at least a source and target property.  Please verify that all edges meet this requirement."

		edge_id = "with source: " + edge["source"] + "and target: " + edge["target"]

        # If edge is directed, it must have a target_arrow_shape
        if "directed" in edge and edge["directed"] == "true":
            if "target_arrow_shape" not in edge:
                return "Edge", edge_id, "must have a target_arrow_shape property if directed is set to true"

        if "source_arrow_shape" in edge:
            error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "mid_source_arrow_shape" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["source_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "target_arrow_shape" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["target_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "mid_target_arrow_shape" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["mid_target_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "line_style" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["line_style"], ALLOWED_EDGE_STYLES)

        if "source_arrow_fill" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["source_arrow_fill"], ALLOWED_ARROW_FILL)

        if "mid_source_arrow_fill" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["mid_source_arrow_fill"], ALLOWED_ARROW_FILL)

        if "target_arrow_fill" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["target_arrow_fill"], ALLOWED_ARROW_FILL)

        if "mid_target_arrow_fill" in edge:
            error +=  find_property_in_array("Edge", edge_id, edge, edge["mid_target_arrow_fill"], ALLOWED_ARROW_FILL)

    if len(error) > 0:
        return error
    else:
        return None

def validate_node_properties(nodes):
    """
    Validates all node properties.

    :param G: NetworkX object.
    """

    unique_ids = set()

    error = ""

    # Go through all nodes to verify if the nodes contain valid properties
    # recognized by CytoscapeJS
    for node in nodes:
        node = node["data"]
    	# Check to see if ID is in node
    	if "id" not in node:
    		return "All nodes must have a unique ID.  Please verify that all nodes meet this requirement."
		
		if node["id"] not in unique_ids:
			unique_ids.add(node["id"])
		else:
			return "There are multiple nodes with ID: " + node["id"] + ".  Please make sure all node IDs are unique."

        # Checks shape of nodes to make sure it contains only legal shapes
        if "shape" in node:
            error += find_property_in_array("Node", node["id"], "shape", node["shape"], ALLOWED_NODE_SHAPES)

        # If node contains a border-style property, check to make sure it is 
        # a legal value
        if "border_style" in node:
            error += find_property_in_array("Node", node["id"], "border_style", node["border_style"], ALLOWED_NODE_BORDER_STYLES)

        # If node contains a background_black property, check to make sure
        # they have values [-1, 1]
        if "border_blacken" in node:
            if node["border_blacken"] >= -1 and node["border_blacken"] <= -1:
                error += "Node: " + node["id"] + " contains illegal border_blacken value.  Must be between [-1, 1]."

        if "background_repeat" in node:
            error += find_property_in_array("Node", node["id"], "background_repeat", node["background_repeat"], ALLOWED_NODE_BACKGROUND_REPEAT)

        if "text_transform" in node:
            error += find_property_in_array("Node", node["id"], "text_transform", node["text_transform"], ALLOWED_NODE_TEXT_TRANSFORM)

        if "text_wrap" in node:
            error += find_property_in_array("Node", node["id"], "text_wrap", node["text_wrap"], ALLOWED_NODE_TEXT_WRAP)

        if "text_background_shape" in node:
            error += find_property_in_array("Node", node["id"], "text_background_shape", node["text_background_shape"], ALLOWED_NODE_SHAPES)

        if "text_halign" in node:
            error += find_property_in_array("Node", node["id"], "text_halign", node["text_halign"], ALLOWED_TEXT_HALIGN)

        if "text_valign" in node:
            error += find_property_in_array("Node", node["id"], "text_valign", node["text_valign"], ALLOWED_TEXT_VALIGN)

    if len(error) > 0:
        return error
    else:
        return None

def find_property_in_array(elementType, key, prop, value, array):
    """
    Goes through array to see if property is contained in the array.

    :param elementType: Node or an Edge
    :param key: Key to search for in network
    :param value: Value of key
    :param prop: Name to search for in array
    :param array: Array to search for property in
    """
    if value not in array:
        array_list = ",".join(array)
        return elementType + " " + key + " contains illegal value for property: " + prop + ".  Value given for this property was: " + value + ".  Accepted values for property: " + prop + " are: [" + array_list + "]"
    else:
        return ""

def assign_edge_ids(json_string):
	'''
		Modifies all ID's of edges to be the names of the nodes that they are attached to.

		:param json_string: JSON of graph
		:return json_string: JSON of graph having unique ID's for all edges
	'''
	
	ids = []
	# Creates ID's for all of the edges by creating utilizing the source and target nodes
	# The edge ID would have the form: source-target
	for edge in json_string['graph']['edges']:

		edge['data']['id'] = edge['data']['source'] + '-' + edge['data']['target']

		# If the ID has not yet been seen (is unique), simply store the ID 
		# of that edge as source-target
		if edge['data']['id'] not in ids:
			ids.append(edge['data']['id'])
		else:
			# Otherwise if there are multiple edges with the same ID,
			# append a number to the end of the ID so we can distinguish
			# multiple edges having the same source and target.
			# This needs to be done because HTML DOM needs unique IDs.
			counter = 0
			while edge['data']['id'] in ids:
				counter += 1
				edge['data']['id'] = edge['data']['id'] + str(counter)
			ids.append(edge['data']['id'])

	# Return JSON having all edges containing unique ID's
	return json_string

# This file is a wrapper to communicate with sqlite3 database 
# that does not need authentication for connection.

# It may be viewed as the controller to the database

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
