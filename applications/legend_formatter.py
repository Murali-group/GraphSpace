import json
import lxml.html

def filter_legend_data(legend_desc_shape, noise):
	filtered_legend = [x for x in legend_desc_shape if x not in noise]
	return filtered_legend

def find_color(root, node_legend_length='none', edge_legend_length='none'):
	color_shape = []
	count = 0
	for element in root.iter('font'):
		count += 1
		x = element.attrib['color'].replace('\"','')
		color_shape.append(x.replace('\\',''))
		if(count == node_legend_length + edge_legend_length):
			return color_shape

def convert_unicode_node_shape(node_shape):
	ACCEPTED_NODE_SHAPES = {u'\u25a0':"rectangle", u'\u25b2':"triangle", u'\u25cf':"circle", u'\u2605': "star", u'\u25fe': "square"}
	new_node_shape = []
	for x in node_shape:
		new_node_shape.append(ACCEPTED_NODE_SHAPES[x])
	return new_node_shape

def convert_unicode_edge_shape(edge_shape):
	ACCEPTED_EDGE_SHAPES  = {u'\u27f6':"triangle", u'\u22a3':"tee", u'\u2014':"none"}
	new_edge_shape = []
	for x in edge_shape:
		new_edge_shape.append(ACCEPTED_EDGE_SHAPES[x])
	return new_edge_shape

def convert_html_legend_1(graph_json,  style_json):
	html_table_string = graph_json['data']['description']
	root = lxml.html.fromstring(html_table_string)
	noise = [u'\xa0\xa0', u'\xa0\xa0\xa0']

	n = 0;
	for tbl in root.xpath('//table'):
		n=n+1
		elements = tbl.xpath('.//tr/td//text()')
		legend_desc_shape = filter_legend_data(elements, noise)
		if n==1:
			node_desc = legend_desc_shape[1::2]
			node_shape = legend_desc_shape[::2]

		if n==2:
			edge_desc = legend_desc_shape[1::2]
			edge_shape = legend_desc_shape[::2]

	elements_color = find_color(root, len(node_shape), len(edge_shape))
	node_color = elements_color[:len(node_shape)]
	edge_color = elements_color[len(edge_shape)-1:]
	node_shape = convert_unicode_node_shape(node_shape)
	edge_shape = convert_unicode_edge_shape(edge_shape)

	legend_json = {}
	legend_json['legend'] = {}
	legend_json['legend']['nodes'] = {}
	legend_json['legend']['edges'] = {}

	for i in range(len(node_desc)):
		legend_json['legend']['nodes'][node_desc[i]] = {}
		legend_json['legend']['nodes'][node_desc[i]]['background-color'] =  node_color[i]
		legend_json['legend']['nodes'][node_desc[i]]['shape'] =  node_shape[i]

	for i in range(len(edge_desc)):
		legend_json['legend']['edges'][edge_desc[i]] = {}
		legend_json['legend']['edges'][edge_desc[i]]['line-color'] =  edge_color[i]
		legend_json['legend']['edges'][edge_desc[i]]['line-style'] =  'solid'
		legend_json['legend']['edges'][edge_desc[i]]['arrow-shape'] =  edge_shape[i]

	style_json.update(legend_json)
	return style_json

def convert_html_legend_2(graph_json,  style_json):
	html_table_string = graph_json['data']['description']
	root = lxml.html.fromstring(html_table_string)

	node_shape_desc = root.xpath('//td//text()');
	node_shape = [node_shape_desc[0],node_shape_desc[2]]

	node_color = []
	for element in root.iter('td'):
		try:
			x = element.attrib['bgcolor'].replace('\"','')
			node_color.append(x.replace('\\',''))

		except:
			pass

	node_color = node_color[2:]
	node_desc = node_shape_desc[5::2]

	legend_json = {};
	legend_json['legend'] = {};
	legend_json['legend']['nodes'] = {};
	legend_json['legend']['edges'] = {};

	for i in range(len(node_desc)):
		legend_json['legend']['nodes'][node_desc[i]] = {};
		legend_json['legend']['nodes'][node_desc[i]]['background-color'] =  node_color[i];
		legend_json['legend']['nodes'][node_desc[i]]['shape'] =  'circle';

	style_json.update(legend_json)
	return style_json
