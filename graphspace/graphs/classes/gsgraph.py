import networkx as nx
import re
from django.utils.datetime_safe import datetime


class GSGraph(nx.DiGraph):
	ALLOWED_NODE_SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
	                       'pentagon', 'hexagon', 'heptagon', 'octagon', 'star',
	                       'diamond', 'vee', 'rhomboid']

	ALLOWED_NODE_BORDER_STYLES = ['solid', 'dotted', 'dashed', 'double']

	ALLOWED_NODE_BACKGROUND_REPEAT = ['no-repeat', 'repeat-x', 'repeat-y', 'repeat']

	ALLOWED_NODE_TEXT_TRANSFORM = ['none', 'uppercase', 'lowercase']

	ALLOWED_NODE_TEXT_WRAP = ['none', 'wrap']

	ALLOWED_TEXT_BACKROUND_SHAPE = ['rectangle', 'roundrectangle']

	ALLOWED_TEXT_HALIGN = ['left', 'center', 'right']

	ALLOWED_TEXT_VALIGN = ['top', 'center', 'bottom']

	## See http://js.cytoscape.org/#style/labels
	ALLOWED_TEXT_WRAP = ['wrap', 'none']

	## See http://js.cytoscape.org/#style/edge-arrow
	ALLOWED_ARROW_SHAPES = ['tee', 'triangle', 'triangle-tee', 'triangle-backcurve',
	                        'square', 'circle', 'diamond', 'none']

	## See http://js.cytoscape.org/#style/edge-line
	ALLOWED_EDGE_STYLES = ['solid', 'dotted', 'dashed']

	ALLOWED_ARROW_FILL = ['filled', 'hollow']

	NODE_COLOR_ATTRIBUTES = ['background-color', 'border-color', 'color',
	                         'text-outline-color', 'text-shadow-color',
	                         'text-border-color']

	EDGE_COLOR_ATTRIBUTES = ['line-color', 'source-arrow-color',
	                         'mid-source-arrow-color', 'target-arrow-color',
	                         'mid-target-arrow-color']

	def __init__(self, *args, **kwargs):
		super(GSGraph, self).__init__(*args, **kwargs)
		self.graph_json = self.compute_graph_json()
		self.style_json = {'style': []}
		self.set_name('Graph ' + datetime.now().strftime("%I:%M%p on %B %d, %Y"))

	def compute_graph_json(self):

		self.graph_json = {
			'data': self.graph,
			'elements': {
				'nodes': [node[1]for node in self.nodes(data=True)],
				'edges': [edge[2] for edge in self.edges(data=True)],
			}
		}

		return self.graph_json

	def get_graph_json(self):
		return self.graph_json

	def get_style_json(self):
		return self.style_json

	def set_graph_json(self, graph_json):
		self.graph_json = graph_json

	def set_style_json(self, style_json):
		GSGraph.validate_style_json(style_json)
		self.style_json = style_json

	def get_name(self):
		return self.graph.get("name", None)

	def set_name(self, name):
		return self.graph.update({"name": name})

	def get_data(self):
		return self.graph

	def set_data(self, data=dict()):
		self.graph.update(data)

	def get_tags(self):
		return self.graph.get("tags", [])

	def set_tags(self, tags):
		return self.graph.update({"tags": tags})

	def add_edge(self, source, target, attr_dict=None, directed=False, popup=None, k=None, **attr):
		attr_dict = attr_dict if attr_dict is not None else dict()
		if 'data' not in attr_dict:
			attr_dict.update({"data": dict()})

		if popup is not None:
			attr_dict['data'].update({"popup": popup})
		if k is not None:
			attr_dict['data'].update({"k": k})

		if attr_dict.get('data').get('is_directed', False) or directed:
			attr_dict.get('data').update({'is_directed': True})
		else:
			attr_dict.get('data').update({'is_directed': False})

		attr_dict.get('data').update({"source": source, "target": target})

		GSGraph.validate_edge_data_properties(data_properties=attr_dict.get('data', dict()), nodes_list=self.nodes())
		super(GSGraph, self).add_edge(source, target, attr_dict)

	def add_node(self, node_name, attr_dict=None, label=None, popup=None, k=None, **attr):
		attr_dict = attr_dict if attr_dict is not None else dict()

		if 'data' not in attr_dict:
			attr_dict.update({"data": dict()})

		if popup is not None:
			attr_dict['data'].update({"popup": popup})
		if k is not None:
			attr_dict['data'].update({"k": k})
		if label is not None:
			attr_dict['data'].update({"label": label})

		attr_dict['data'].update({"name": node_name, "id": node_name})

		GSGraph.validate_node_data_properties(data_properties=attr_dict.get('data', dict()), nodes_list=self.nodes())
		super(GSGraph, self).add_node(node_name, attr_dict)

	def add_node_style(self, node_name, attr_dict=None, content=None, shape='ellipse', color='#FFFFFF', height=None,
	                                   width=None, bubble=None, valign='center', halign='center', style="solid",
	                                   border_color='#000000', border_width=1):
		"""
		Add the style for the given node in the style json.

		Parameters
		----------
		node_name: string - name of the node.
		shape: string -- shape of node. Default = "ellipse".
		color: string -- hexadecimal representation of the color (e.g., #FFFFFF) or color name. Default = white.
		height: int -- height of the node's body. Use None to determine height from the number of lines in the label. Default = None.
		width: int -- width of the node's body, or None to determine width from length of label.  Default=None.
		bubble: string -- color of the text outline. Using this option gives a "bubble" effect; see the bubbleeffect() function. Optional.
		valign: string -- vertical alignment. Default = center.
		halign: string -- horizontal alignment. Default = center.
		style: string -- style of border. Default is "solid".  If Bubble is specified, then style is overwritten.
		border_color: string -- color of border. Default is #000000. If Bubble is specified, then style is overwritten.
		border_width: int -- width of border. Default is 4.  If Bubble is specified, then style is overwritten.


		Returns
		-------
		None

		"""
		attr_dict = attr_dict if attr_dict is not None else dict()

		selector = 'node[name="%s"]' % node_name

		style_properties = {}
		style_properties = GSGraph.set_node_shape_property(style_properties, shape)
		style_properties = GSGraph.set_node_color_property(style_properties, color)
		style_properties = GSGraph.set_node_label_property(style_properties, content)
		style_properties = GSGraph.set_node_width_property(style_properties, width)
		style_properties = GSGraph.set_node_height_property(style_properties, height)
		style_properties = GSGraph.set_node_vertical_alignment_property(style_properties, valign)
		style_properties = GSGraph.set_node_horizontal_alignment_property(style_properties, halign)
		style_properties = GSGraph.set_node_border_style_property(style_properties, style)
		style_properties = GSGraph.set_node_border_color_property(style_properties, border_color)
		style_properties = GSGraph.set_node_border_width_property(style_properties, border_width)

		# If bubble is specified, use the provided color,
		if bubble:
			style_properties = GSGraph.set_node_bubble_effect_property(style_properties, bubble, whitetext=False)

		attr_dict.update(style_properties)

		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': attr_dict
			}]
		})

	def add_edge_style(self, source, target, attr_dict=None, directed=False, color='#000000', width=1.0, arrow_shape='triangle',
	                   edge_style='solid', arrow_fill='filled'):
		"""
		Add the style for the given edge in the style json.

		source: string -- unique ID of the source node
		target: string -- unique ID of the target node
		color: string -- hexadecimal representation of the color (e.g., #000000), or the color name. Default = black.
		directed: bool - if True, draw the edge as directed. Default = False.
		width: float -- width of the edge.  Default = 1.0
		arrow_shape: string -- shape of arrow head. Default is "triangle"
		edge_style: string -- style of edge. Default is "solid"
		arrow_fill: string -- fill of arrow. Default is "filled"

		Returns
		-------
		None

		"""
		data_properties = {}
		style_properties = {}
		data_properties.update({"source": source, "target": target})
		style_properties = GSGraph.set_edge_color_property(style_properties, color)
		style_properties = GSGraph.set_edge_width_property(style_properties, width)
		style_properties = GSGraph.set_edge_target_arrow_shape_property(style_properties, arrow_shape)
		style_properties = GSGraph.set_edge_directionality_property(style_properties, directed, arrow_shape)
		style_properties = GSGraph.set_edge_line_style_property(style_properties, edge_style)
		style_properties = GSGraph.set_edge_target_arrow_fill(style_properties, arrow_fill)

		attr_dict = attr_dict if attr_dict is not None else dict()

		selector = 'edge[source="%s"][target="%s"]' % (source, target)

		attr_dict.update(style_properties)

		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': attr_dict
			}]
		})




	####################################################################
	### NODE PROPERTY FUNCTIONS #################################################


	@staticmethod
	def set_node_label_property(node_properties, label):
		"""
		Set the label "label" to a "node_properties" dict and return the "node_properties" dict.
		The label is stored under "content" in the node information. Also set wrap = 'wrap' so newlines are interpreted.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.
		label - text to display on node. "\n" will be interpreted as a newline.

		Returns
		-------
		Dictionary of node attributes.

		"""
		if label is not None:
			node_properties.update({'content': label})
		node_properties = GSGraph.set_node_wrap_property(node_properties, 'wrap')

		return node_properties

	@staticmethod
	def set_node_wrap_property(node_properties, wrap):
		"""
		Adding node wrap allows the newline '\n' to be interpreted as a line break for the node.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.
		wrap - string denoting the type of wrap: one of "wrap" or "none".

		Returns
		-------
		Dictionary of node attributes.

		Raises
		-------

		Exception - if the wrap parameter is not one of the allowed wrap styles. See ALLOWED_NODE_TEXT_WRAP for more details.

		"""
		if wrap not in GSGraph.ALLOWED_NODE_TEXT_WRAP:
			raise Exception('"%s" is not an allowed text wrap style.' % (wrap))
		node_properties.update({'text-wrap': wrap})
		return node_properties

	@staticmethod
	def set_node_shape_property(node_properties, shape):
		"""
		Add a shape property "shape" to the node_properties.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.
		shape - string -- shape of node. Default = "ellipse".

		Returns
		-------
		Dictionary of node attributes.

		Raises
		-------

		Exception - if the shape is not one of the allowed node shapes. See ALLOWED_NODE_SHAPES global variable.

		"""
		if shape not in GSGraph.ALLOWED_NODE_SHAPES:
			raise Exception('"%s" is not an allowed shape.' % (shape))
		node_properties.update({'shape': shape})
		return node_properties

	@staticmethod
	def set_node_color_property(node_properties, color):
		"""
		Add a background color to the node_properties.
		Color can be a name (e.g., 'black') or an HTML string (e.g., #00000).


		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.
		color - string -- hexadecimal representation of the color (e.g., #FFFFFF) or color name.

		Returns
		-------
		Dictionary of node attributes.

		Raises
		-------

		Exception - if the color is improperly formatted.

		"""
		error = GSGraph.check_color_hex(color)
		if error is not None:
			raise Exception(error)
		node_properties.update({'background-color': color})
		return node_properties

	@staticmethod
	def set_node_height_property(node_properties, height):
		"""
		Add a node height property to the node_properties.
		If the height is 'None', then the height of the node is determined by the number of newlines in the label that will be displayed.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.
		height - int -- height of the node's body. Use None to determine height from the number of lines in the label.

		Returns
		-------
		Dictionary of node attributes.

		"""
		if height == None:
			height = 'label'

		node_properties.update({'height': height})
		return node_properties

	@staticmethod
	def set_node_width_property(node_properties, width):
		"""
		Add a node width property to the node_properties.
		If the width is 'None', then the width of the node is determined by the length of the label.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.
		width - int -- width of the node's body, or None to determine width from length of label.

		Returns
		-------
		Dictionary of node attributes.

		"""
		if width == None:
			## take the longest width of the label after interpreting newlines.
			width = 'label'
		node_properties.update({'width': width})
		return node_properties

	@staticmethod
	def set_node_bubble_effect_property(node_properties, color, whitetext=False):
		"""
		Add a "bubble effect" to the node by making the
		border color the same as the text outline color.

		Parameters
		----------
		whitetext - Boolean -- if True, text is colored white instead of black. Default is False.
		color - string -- hexadecimal representation of the text outline color (e.g., #FFFFFF) or a color name.
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.

		Returns
		-------
		Dictionary of node attributes.

		"""
		node_properties.update({'text-outline-color': color})
		node_properties = GSGraph.set_node_border_color_property(node_properties, color)
		# also make outline thicker and text larger
		node_properties.update({'text-outline-width': 4})
		if whitetext:
			node_properties.update({'color': 'white'})
		return node_properties

	@staticmethod
	def set_node_border_width_property(node_properties, border_width):
		"""
		Set the border width in node_properties.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.

		Returns
		-------
		Dictionary of node attributes.

		"""
		node_properties.update({'border-width': border_width})
		return node_properties

	@staticmethod
	def set_node_border_style_property(node_properties, border_style):
		"""
		Set the border width in node_properties.

		Parameters
		----------
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.

		Returns
		-------
		Dictionary of node attributes.

		Raises
		-------

		Exception - if the border_style parameter is not one of the allowed border styles. See ALLOWED_NODE_BORDER_STYLES for more details.


		"""
		if border_style not in GSGraph.ALLOWED_NODE_BORDER_STYLES:
			raise Exception('"%s" is not an allowed node border style.' % (border_style))
		node_properties.update({'border-style': border_style})
		return node_properties

	@staticmethod
	def set_node_border_color_property(node_properties, border_color):
		"""
		Set the border_color in node_properties.

		Parameters
		----------
		color - string -- hexadecimal representation of the text outline color (e.g., #FFFFFF) or a color name.
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.

		Returns
		-------
		Dictionary of node attributes.

		Raises
		-------

		Exception - if the border_color is improperly formatted.


		"""
		error = GSGraph.check_color_hex(border_color)
		if error is not None:
			raise Exception(error)
		node_properties.update({'border-color': border_color})
		return node_properties

	@staticmethod
	def set_node_vertical_alignment_property(node_properties, valign):
		"""
		Set the vertical alignment of label in node_properties.

		Parameters
		----------
		valign - string -- alignment of text.
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.

		Returns
		-------
		Dictionary of node attributes.

		"""

		node_properties.update({'text-valign': valign})
		return node_properties

	@staticmethod
	def set_node_horizontal_alignment_property(node_properties, halign):
		"""
		Set the horizontal alignment of label in node_properties.

		Parameters
		----------
		valign - halign -- alignment of text.
		node_properties - Dictionary of node attributes.  Key/value pairs will be used to set data associated with the node.

		Returns
		-------
		Dictionary of node attributes.

		"""

		node_properties.update({'text-halign': halign})
		return node_properties


	####################################################################
	### EDGE PROPERTY FUNCTIONS #################################################

	@staticmethod
	def set_edge_color_property(edge_properties, color):
		"""
		Add a edge color to the edge_properties.

		Color both the line and the target arrow; if the edge
		is undirected, then the target arrow color doesn't matter.
		If it's directed, then the arrow color will match the line color.

		Color can be a name (e.g., 'black') or an HTML string (e.g., #00000).

		Parameters
		----------
		edge_properties - Dictionary of edge attributes.  Key/value pairs will be used to set data associated with the edge.
		color - string -- hexadecimal representation of the color (e.g., #FFFFFF) or color name.

		Returns
		-------
		Dictionary of edge attributes.

		Raises
		-------

		Exception - if the color is improperly formatted.

		"""
		error = GSGraph.check_color_hex(color)
		if error is not None:
			raise Exception(error)

		edge_properties.update({'line-color': color})
		edge_properties.update({'target-arrow-color': color})
		return edge_properties

	@staticmethod
	def set_edge_directionality_property(edge_properties, directed, arrow_shape='triangle'):
		"""
		Sets a target arrow shape.

		Parameters
		----------
		edge_properties - Dictionary of edge attributes.  Key/value pairs will be used to set data associated with the edge.
		directed - bool - if True, draw the edge as directed.
		arrow_shape - string -- shape of arrow. See ALLOWED_ARROW_SHAPES.

		Returns
		-------
		Dictionary of edge attributes.

		"""
		if directed:
			edge_properties = GSGraph.set_edge_target_arrow_shape_property(edge_properties, arrow_shape)
		else:
			edge_properties = GSGraph.set_edge_target_arrow_shape_property(edge_properties, 'none')
		return edge_properties

	@staticmethod
	def set_edge_width_property(edge_properties, width):
		"""
		Sets the width property of the edge.

		Parameters
		----------
		edge_properties - Dictionary of edge attributes.  Key/value pairs will be used to set data associated with the edge.
		width - float -- width of the edge.  Default = 1.0

		Returns
		-------
		Dictionary of edge attributes.

		"""
		edge_properties.update({'width': width})
		return edge_properties

	@staticmethod
	def set_edge_target_arrow_shape_property(edge_properties, arrow_shape):
		"""
		Assigns an arrow shape to edge

		Parameters
		----------
		edge_properties - Dictionary of edge attributes.  Key/value pairs will be used to set data associated with the edge.

		Returns
		-------
		Dictionary of edge attributes.

		"""
		edge_properties.update({'target-arrow-shape': arrow_shape})
		return edge_properties

	@staticmethod
	def set_edge_line_style_property(edge_properties, style):
		"""
		Adds the edge line style to edge

		Parameters
		----------
		edge_properties - Dictionary of edge attributes.  Key/value pairs will be used to set data associated with the edge.
		style - string -- style of line

		Returns
		-------
		Dictionary of edge attributes.

		"""
		edge_properties.update({'line-style': style})
		return edge_properties

	@staticmethod
	def set_edge_target_arrow_fill(edge_properties, fill):
		"""
		Adds the arrowhead fill to edge

		Parameters
		----------
		edge_properties - Dictionary of edge attributes.  Key/value pairs will be used to set data associated with the edge.
		fill - string -- fill of arrowhead.

		Returns
		-------
		Dictionary of edge attributes.

		"""
		edge_properties.update({'target-arrow-fill': fill})
		return edge_properties

	@staticmethod
	def check_color_hex(color_code):
		"""
		Check the validity of the hexadecimal code of various node and edge color
		related attributes.

		This function returns an error if the hexadecimal code is not of the format
		'#XXX' or '#XXXXXX', i.e. hexadecimal color code is not valid.

		:param color_code: color code
		"""
		# if color name is given instead of hex code, no need to check its validity
		if not color_code.startswith('#'):
			return None
		valid = re.search(r'^#(?:[0-9a-fA-F]{1}){3,6}$', color_code)
		if valid is None:
			return color_code + ' is not a valid hex color code.'
		else:
			return None

	@staticmethod
	def validate_property(element, element_selector, property_name, valid_property_values):
		"""
		Goes through array to see if property is contained in the array.

		Parameters
		----------
		element: Element to search for in network
		element_selector: selector for element in the network
		property_name: name of the property
		valid_property_values: List of valid properties

		Returns
		-------
		None - if the property is valid or does not exist
		Error message - if the property is not valid

		"""
		if property_name in element and element[property_name] not in valid_property_values:
			return element_selector + " contains illegal value for property: " + property_name + ".  Value given for this property was: " + \
			       element[
				       property_name] + ".  Accepted values for property: " + property_name + " are: [" + valid_property_values + "]"

		return None

	@staticmethod
	def validate_node_data_properties(data_properties, nodes_list):
		"""
		Validates the data properties.

		Parameters
		----------
		data_properties: dict of node data properties
		nodes_list: list of nodes.

		Returns
		-------
		None - if node_properties are valid

		Raises
		--------
		Raises an exception - if properties are not valid.

		"""

		# Check to see if name is in node_properties
		if "name" not in data_properties:
			raise Exception("All nodes must have a unique name.  Please verify that all nodes meet this requirement.")

		# Check the data type of node_properties, should be int, float or string
		if not isinstance(data_properties["name"], (basestring, int, float)):
			raise Exception("All nodes must be strings, integers or floats")

		if data_properties["name"] in nodes_list:
			raise Exception("There are multiple nodes with name: " + str(
				data_properties["name"]) + ".  Please make sure all node names are unique.")

	@staticmethod
	def validate_style_properties(style_properties, selector):
		"""
		Validates the style properties.

		Parameters
		----------
		style_properties: dict of elements style properties
		selector: selector for the element

		Returns
		-------
		None - if node_properties are valid

		Raises
		--------
		Raises an exception - if properties are not valid.

		Notes
		-----

		Refer to http://js.cytoscape.org/#selectors for selectors.

		"""
		error_list = []

		# This list contains tuple values (property_name, allowed_property_values) where property_name is the name of the property to be checked and
		# allowed_property_values is the list of allowed or legal values for that property.
		node_validity_checklist = [
			# Node specific
			("shape", GSGraph.ALLOWED_NODE_SHAPES),
			("border-style", GSGraph.ALLOWED_NODE_BORDER_STYLES),
			("background-repeat", GSGraph.ALLOWED_NODE_BACKGROUND_REPEAT),
			("text-transform", GSGraph.ALLOWED_NODE_TEXT_TRANSFORM),
			("text-wrap", GSGraph.ALLOWED_NODE_TEXT_WRAP),
			("text-background-shape", GSGraph.ALLOWED_NODE_SHAPES),
			("text-halign", GSGraph.ALLOWED_TEXT_HALIGN),
			("text-valign", GSGraph.ALLOWED_TEXT_VALIGN),
			# Edge specific
			("source-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("mid-source-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("target-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("mid-target-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("line-style", GSGraph.ALLOWED_EDGE_STYLES),
			("source-arrow-fill", GSGraph.ALLOWED_ARROW_FILL),
			("mid-source-arrow-fill", GSGraph.ALLOWED_ARROW_FILL),
			("target-arrow-fill", GSGraph.ALLOWED_ARROW_FILL),
			("mid-target-arrow-fill", GSGraph.ALLOWED_ARROW_FILL)
		]

		for property_name, allowed_property_values in node_validity_checklist:
			error = GSGraph.validate_property(style_properties, selector, property_name, allowed_property_values)
			if error is not None:
				error_list.append(error)

		# If style_properties contains a background_black property, check to make sure they have values [-1, 1]
		if "border-blacken" in style_properties and -1 <= style_properties["border-blacken"] <= 1:
			error_list.append(selector + " contains illegal border-blacken value.  Must be between [-1, 1].")

		for attr in GSGraph.NODE_COLOR_ATTRIBUTES + GSGraph.EDGE_COLOR_ATTRIBUTES:
			if attr in style_properties:
				error = GSGraph.check_color_hex(style_properties[attr])
				if error is not None:
					error_list.append(error)

		if len(error_list) > 0:
			raise Exception(", ".join(error_list))
		else:
			return None

	@staticmethod
	def validate_edge_data_properties(data_properties, nodes_list):
		"""
		Validates the data properties.

		Parameters
		----------
		data_properties: dict of edge data properties
		nodes_list: list of nodes.

		Returns
		-------
		None - if edge_properties are valid

		Raises
		--------
		Raises an exception - if properties are not valid.

		"""

		# Go through all edge properties to verify if edges contain valid properties recognized by CytoscapeJS

		# If edge has no source and target nodes, throw error since they are required
		if "source" not in data_properties or "target" not in data_properties:
			raise Exception(
				"All edges must have at least a source and target property.  Please verify that all edges meet this requirement.")

		# Check if source and target node of an edge exist in the node list
		if data_properties["source"] not in nodes_list or data_properties["target"] not in nodes_list:
			raise Exception("For all edges source and target nodes should exist in node list")

		# Check if source and target nodes are strings, integers or floats
		if not (isinstance(data_properties["source"], (basestring, int, float)) and isinstance(
					data_properties["target"],
					(basestring, int, float))):
			raise Exception("Source and target nodes of the edge must be strings, integers or floats")

		if "is_directed" not in data_properties:
			raise Exception("All edges must have a `is_directed` property.  Please verify that all edges meet this requirement.")

		# Check the data type of node_properties, should be int
		if not isinstance(data_properties["is_directed"], (int)) or (data_properties["is_directed"] > 1):
			raise Exception("All is_directed properties must be integers. Valid values are 0 or 1.")

	@staticmethod
	def validate_style_json(style_json):
		if type(style_json) is list:
			for json in style_json:
				GSGraph.validate_style_json(json)
		else:
			for elem in style_json.get('style', []):
				if 'css' in elem:
					GSGraph.validate_style_properties(elem['selector'], elem['css'])
				else:
					GSGraph.validate_style_properties(elem['selector'], elem['style'])

