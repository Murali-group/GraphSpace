## GPML Parser using Interface
## Divit Singh, Anna Ritz, Allison Tegge, and T. M. Murali
## Contact: T. M. Murali (murali@cs.vt.edu)
## License: GPL version 3
##
## GraphSpace programmer's guide on the Help page: 
## http://graphspace.org/help/programmers/
##
## This python file contains functions to parse GPML file and create
## a NetworkX Directed Graph object using the graphspace interface.
## GPML format supports various forms of elements, we parse the file
## to extract all Shapes, Labels, DataNodes, Groups and Interaction
## elements. Shapes, Labels, Datanodes and Groups are treated as nodes
## and Interactions are treated as edges to create the network.
## We follow the GraphSpace JSON spec to add attributes to nodes and
## edges.


from graphspace_interface import graphspace_interface as interface
import networkx as nx
import json
import xml.etree.ElementTree as ET


# Current supported GPML format
GPML = '{http://pathvisio.org/GPML/2013a}'


def parse_gpml(graph_gpml, title):
    """ Parse the GPML file.

    This is the driver function for parsing the GPML file. We go
    through the GPML file using the Python XML paser as the GPML
    format is based on XML. We parse different elements of the
    file and build a NetworkX Directed Graph from the GPML file.

    We use the convertNXtoDict function from the graphspace
    interface to convert the Graph object to a dictionary which
    resembles the JSON structure recoginsed by GraphSpace. 
    
    :param graph_gpml: The GPML file.
    :param title: title of the graph/network

    """

    # Create a directed NetworkX graph to store the attributes of
    # datanodes, shapes, labels, groups and interactions.
    G = nx.DiGraph(directed=True)

    # Use xml parser to parse the GPML file
    graph_gpml = ET.fromstring(graph_gpml)

    # Parsing the GPML file for Group elements.
    # This is the first step because 
    G = parse_groups(G, graph_gpml)

    # Parsing the GPML file for Shape elements
    G = parse_shapes(G, graph_gpml)

    # Parsing the GPML file for DataNode elements
    G = parse_datanodes(G, graph_gpml)

    # Parsing the GPML file for Label elements
    G = parse_labels(G, graph_gpml)

    # This is a crude version of getting interactions (edges) working
    # Look for all the interactions
    interactions =  graph_gpml.findall(GPML+'Interaction')
    G = parse_interactions(G, interactions)

    # Set the layout of the GPML file. This is an important
    # step as GraphSpace by default will create a random
    # layout for every graph. We parse through the x and y
    # coordinates of elements as specified in the GPML file.
    layout = set_gpml_layout(G)

    # add metadata to the graph
    metadata = {'description':'','title':  graph_gpml.attrib['Name'] or "GPML",'tags':[]}
    title = title or metadata['title']

    # Convert the graph created to a dictionary.
    parse_json = interface.convertNXToDict(G, metadata=metadata)

    return parse_json, layout, title


def parse_shapes(G, graph_gpml):
    # Create a list of details of all the shape
    shapes =  graph_gpml.findall(GPML+'Shape')

    shape_attributes = _extract_attributes(shapes)

    # Add shape elemets to the JSON structure parse_json
    for node in shape_attributes:
        temp_node = {'data': {}}
        # The GraphId attribute for every element is unique.
        # Hence we use this attribute for node_id field of add_node()
        interface.add_node(G, node['GraphId'])

        G = update_node_graphics(G, node['GraphId'], node)

        # Deal with the ShapeType field of the shape element,
        # improve this, make it more general, too many hacks right now.
        if 'ShapeType' in node:
            shape_type = node['ShapeType'].lower()
            if shape_type == 'brace' or shape_type == 'arc':
                interface.add_node_shape(G, node['GraphId'], 'rectangle')
            else:
                # oval in GPML is ellipse in cytoscape JSON
                if shape_type == 'oval':
                    interface.add_node_shape(G, node['GraphId'], 'ellipse')
                # roundedrectangle in GPML is roundrectangle in cytoscape JSON
                elif shape_type == 'roundedrectangle':
                    interface.add_node_shape(G, node['GraphId'], 'roundrectangle')
                # everything else works right now, may break with more testing
                else:
                    interface.add_node_shape(G, node['GraphId'], 'roundrectangle')
        else:
            # if no ShapeType given use rectangle by default.
            interface.add_node_shape(G, node['GraphId'], 'rectangle')

        # this has to be zero because we'll have multiple elements
        if 'key' in node:
            if node['key'] == 'org.pathvisio.DoubleLineProperty':
                interface.add_node_border_style(G, node['GraphId'], 'double')
    return G


def parse_datanodes(G, graph_gpml):
    # Parsing the DataNode element for all the details.
    datanodes =  graph_gpml.findall(GPML+'DataNode')
    node_attributes = _extract_attributes(datanodes)

    # Go through the node details of the node
    for node in node_attributes:
        # Give an id to the node element.
        interface.add_node(G, node['GraphId'], shape='rectangle', border_width=2)
        # Parse through the 
        G = update_node_graphics(G, node['GraphId'], node)

        # if 'Color' in node:
        #     interface.add_node_border_color(G, node['GraphId'], '#' + node['Color'])
        #     interface.add_node_fill_color(G, node['GraphId'], '#' + node['Color'])

        interface.add_node_color(G, node['GraphId'], 'white')
        interface.add_node_background_opacity(G, node['GraphId'], 0)

        # We use compound nodes to represent GPML groups in GraphSpace.
        if 'GroupRef' in node:
            for group in G.nodes_iter(data=True):
                if 'group_id' in group[1]:
                    if group[1]['group_id'] == node['GroupRef']:
                        parent = group[0]
                        interface.add_node_parent(G, node['GraphId'], parent)
    return G


def parse_labels(G, graph_gpml):
    # Parsing the label element for all the details.
    labels =  graph_gpml.findall(GPML+'Label')

    label_attributes = _extract_attributes(labels)

    for node in label_attributes:
        temp_node = {'data': {}}
        interface.add_node(G, node['GraphId'], border_color='#FFFFFF')
        update_node_graphics(G, node['GraphId'], node)

    return G


def parse_interactions(G, interactions):
    # Create a list of (x, y) coordinates of an edge
    # every element of the list can be either of length of 2 or 3
    # as curved edges are represented by 3 coordinates.

    # edge_details = []
    # for edge in interactions:
    #     for details in edge:
    #         temp_edge = []
    #         for more in details:
    #             # if 'X' in more.attrib and 'Y' in more.attrib and 'g:
    #             #     temp_edge.append((more.attrib['X'], more.attrib['Y']))
    #             if 'GraphRef' in more.attrib:
    #                 temp_edge.append(more.attrib['GraphRef'])

    #         edge_details.append(temp_edge)     

    edge_attributes = []
    for edge in interactions:
        temp_edge = {}
        temp_edge.update(edge.attrib)
        list_of_points = []
        for nested_layer_attribute in edge:
            temp_edge.update(nested_layer_attribute.attrib)
            for points in nested_layer_attribute:
                list_of_points.append(points.attrib)

            temp_edge['points'] = list_of_points
        edge_attributes.append(temp_edge)

            
    # print edge_attributes

    edges = []
    for edge in edge_attributes:
        temp = []
        for point in edge['points']:
            if 'GraphRef' in point:
                temp.append(point['GraphRef'])
        edges.append(temp)

    for edge in edges:
        if len(edge) > 1:
            interface.add_edge(G, edge[0], edge[1])



    # the above way of adding attributes will append after every empty list
    # something like [['something'], [], ['more'], [], ['something']]
    # that's why we use the magic of list slicing [::2]
    # create temp edge ids
    # temp_edge_ids = []
    # for edge in edge_details[::2]:
    #     edge_id = []
    #     for nodes in edge:
    #         temp_node = {'data': {}}
    #         interface.add_node(G, count)
    #         edge_id.append(count)
    #         interface.add_node_x_coordinate(G, count, nodes[0])
    #         interface.add_node_y_coordinate(G, count, nodes[1])
    #         interface.add_node_color(G, count, 'white')
    #         interface.add_node_background_opacity(G, count, 0)
    #         count = count + 1
    #     temp_edge_ids.append(edge_id)

    # create edges
    # TODO: extract more information from edges, i.e arrow shapes
    # right now by default we are using triangle as arrow shape.
    # for edge in temp_edge_ids:
    #     temp_edge = {'data': {}}
    #     if len(edge) == 2:
    #         interface.add_edge(G, edge[0], edge[1])
    #         interface.add_edge_target_arrow_shape(G, edge[0], edge[1], 'triangle')
    #     if len(edge) == 3:
    #         interface.add_edge(G, edge[0], edge[1])
    #         interface.add_edge_target_arrow_shape(G, edge[0], edge[1], 'triangle')

    #         temp_edge = {'data': {}}
    #         interface.add_edge(G, edge[1], edge[2])

    # This is the where magic happens, creating the layout
    # for the GPML file.
    return G


def set_gpml_layout(G):
    default_layout = []
    for node in G.nodes_iter(data=True):
        if 'x' in node[1] and 'y' in node[1]:
            temp = dict()
            temp['id'] = str(node[0])
            temp['x'] = float(node[1]["x"])
            temp['y'] = float(node[1]["y"])
            default_layout.append(temp)

    # Well, we need it in JSON format. So ..
    default_layout = json.dumps(default_layout)
    return default_layout


def parse_groups(G, graph_gpml):
    groups =  graph_gpml.findall(GPML+'Group')
    for group in groups:
        temp_node = {'data': {}}
        interface.add_node(G, group.attrib['GraphId'])
        interface.add_node_group_id(G, group.attrib['GraphId'], group.attrib['GroupId'])
        interface.add_node_color(G,group.attrib['GraphId'], 'white')
        interface.add_node_border_color(G, group.attrib['GraphId'], 'black')
    return G


def update_node_graphics(G, node_id, node):
    if 'CenterX' in node and 'CenterY' in node:
        interface.add_node_x_coordinate(G, node['GraphId'], node['CenterX'])
        interface.add_node_y_coordinate(G, node['GraphId'], node['CenterY'])
    else:
        return {"Error": "GPML file must contain X and Y coordinates"
                "of all the node type elements! Value for node"
                + str(node['GraphId']) + " missing"}
    
    if 'Height' in node:
        interface.add_node_height(G, node['GraphId'], node['Height'])

    if 'Width' in node:
        interface.add_node_width(G, node['GraphId'], node['Width'])

    if 'Align' in node:
        interface.add_node_horizontal_alignment(G, node['GraphId'], node['Align'], gpml=True)

    if 'Valign' in node:
        interface.add_node_vertical_alignment(G, node['GraphId'], node['Valign'], gpml=True)

    if 'TextLabel' in node:
        interface.add_node_label(G, node['GraphId'], node['TextLabel'])

    if 'FontSize' in node:
        interface.add_node_fontsize(G, node['GraphId'], node['FontSize'])

    if 'LineThickness' in node:
        interface.add_node_border_width(G, node['GraphId'], node['LineThickness'])

    # this is the twist out here, if you compare this with node color
    # attribute, we use the color given for border_color rather than
    # color (i.e. text color)  
    if 'Color' in node:
        interface.add_node_border_color(G, node['GraphId'], '#' + node['Color'])
    if 'FillColor' in node:
        interface.add_node_color(G, node['GraphId'], '#' + node['FillColor'])
    else:
        interface.add_node_color(G, node['GraphId'], 'white')

    interface.add_node_background_opacity(G, node['GraphId'], 0)


    return G


def _extract_attributes(nodes):
    node_attributes = []
    for node in nodes:
        temp_node = {}
        temp_node.update(node.attrib)
        for nested_layer_attribute in node:
            temp_node.update(nested_layer_attribute.attrib)
        node_attributes.append(temp_node)
    return node_attributes
