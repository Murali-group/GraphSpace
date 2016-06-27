import graphspace_interface as interface
import networkx as nx
import json
import xml.etree.ElementTree as ET


# Current supported GPML format
GPML = '{http://pathvisio.org/GPML/2013a}'


def parse_gpml(graph_json, title):
    """ Parse the GPML file

    """
    # Create a directed NetworkX graph to parse through
    G = nx.DiGraph(directed=True)
    
    # Use xml parser to parse the GPML file
    graph_gpml = ET.fromstring(graph_json)
    # Keep the overall count of nodes and create unique ids for
    # datanodes, shape, labels.
    # IMPORTANT!!!
    count = 0

    # Parsing the GPML file for Shape elements
    G, count = parse_shapes(G, count, graph_gpml)

    # Find all the DataNodes in the GPML file which is used to draw various
    # the various nodes of the graph
    G, count = parse_datanodes(G, count, graph_gpml)
    # Parsing the GPML file for Shape elements
    labels =  graph_gpml.findall(GPML+'Label')
    G, count = parse_labels(G, count, labels)
    # This is a crude version of getting interactions (edges) working
    # Look for all the interactions
    interactions =  graph_gpml.findall(GPML+'Interaction')
    G, count = parse_interactions(G, count, interactions)
    layout = set_gpml_layout(G)

    # To add nodes to the group we parse through the group
    # elements of the GPML file.
    groups =  graph_gpml.findall(GPML+'Group')
    G = parse_groups(G, groups)

    
    metadata = {'description':'','title':  graph_gpml.attrib['Name'] or "GPML",'tags':[]}
    title = title or metadata['title']
    parse_json = interface.convertNXToDict(G, metadata=metadata)

    return parse_json, layout, title


def parse_shapes(G, count,  graph_gpml):
    # Create a list of details of all the shape
    shapes =  graph_gpml.findall(GPML+'Shape')
    shape_details = []
    for shape in shapes:
        temp_node = {}
        temp_node.update(shape.attrib)
        for more_details in shape:
            temp_node.update(more_details.attrib)
        shape_details.append(temp_node)
    # Add shape elemets to the JSON structure parse_json
    for node in shape_details:
        temp_node = {'data': {}}
        # Give an id to the shape element.
        interface.add_node(G, count)
        _node_graphics(G, count, node)

        # Shape element may or may not contain a TextLabel field
        if 'TextLabel' in node:
            interface.add_node_label(G, count, node['TextLabel'])

        # Deal with the ShapeType field of the shape element,
        # improve this, make it more general, too many hacks right now.
        if 'ShapeType' in node:
            shape_type = node['ShapeType'].lower()
            if shape_type == 'brace' or shape_type == 'arc':
                interface.add_node_shape(G, count, 'rectangle')
            else:
                # oval in GPML is ellipse in cytoscape JSON
                if shape_type == 'oval':
                    interface.add_node_shape(G, count, 'ellipse')
                # roundedrectangle in GPML is roundrectangle in cytoscape JSON
                elif shape_type == 'roundedrectangle':
                    interface.add_node_shape(G, count, 'roundrectangle')
                # everything else works right now, may break with more testing
                else:
                    interface.add_node_shape(G, count, 'roundrectangle')
        else:
            # if no ShapeType given use rectangle by default.
            interface.add_node_shape(G, count, 'rectangle')
        # this is the twist out here, if you compare this with node color
        # attribute, we use the color given for border_color rather than
        # color (i.e. text color)
        if 'Color' in node:
            temp_node['data']['border_color'] = '#' + node['Color']
        if 'FillColor' in node:
            interface.add_node_color(G, count, '#' + node['FillColor'])
        else:
            interface.add_node_color(G, count, 'white')
        # this has to be zero because we'll have multiple elements
        interface.add_node_background_opacity(G, count, 0)
        if 'key' in node:
            if node['key'] == 'org.pathvisio.DoubleLineProperty':
                interface.add_node_border_style(G, count, 'double')
        if 'LineThickness' in node:
            interface.add_node_border_width(G, count, node['LineThickness'])
        else:
            interface.add_node_border_width(G, count, 1)
        # increase count, i.e. to keep unique ids for shapes, nodes, labels.
        count = count + 1
    return G, count


def parse_datanodes(G, count, graph_gpml):
    # Parsing the DataNode element for all the details.
    datanodes =  graph_gpml.findall(GPML+'DataNode')
    node_details = []
    for node in datanodes:
        temp = {}
        temp = node.attrib
        for details in node:
            temp.update(details.attrib)
        node_details.append(temp)
    # Go through the node details of the node
    for node in node_details:
        temp_node = {'data': {}}

        # Give an id to the node element.
        interface.add_node(G, count)
        _node_graphics(G, count, node)

        # Not sure about text label. Haven't got an error yet for textlable
        # YET!!
        interface.add_node_label(G, count, node['TextLabel'])
        # temp_node['data']['content'] = node['TextLabel']

        # Again not sure about font size
        # temp_node['data']['font_size'] = node['FontSize']
        interface.add_node_fontsize(G, count, node['FontSize'])

        if 'Color' in node:
            interface.add_node_border_color(G, count, '#' + node['Color'])
            interface.add_node_fill_color(G, count, '#' + node['Color'])
            # temp_node['data']['color'] = '#' + node['Color']
            # temp_node['data']['border_color'] = '#' + node['Color']
        interface.add_node_color(G, count, 'white')
        # temp_node['data']['background_color'] = 'white'
        interface.add_node_background_opacity(G, count, 0)
        # temp_node['data']['background_opacity'] = 0

        # temp_node['data']['border_width'] = 2
        # rectangle is the default shape for all the datanodes
        interface.add_node_shape(G, count, 'rectangle')
        # temp_node['data']['shape'] = 'rectangle'
        # We use compound nodes to represent GPML groups in GraphSpace.
        if 'GroupRef' in node:
            interface.add_node_parent(G, count, node['GroupRef'])
            # temp_node['data']['parent'] = node['GroupRef']

        # increase count, i.e. to keep unique ids for shapes, nodes, labels.
        count = count + 1
    return G, count


def parse_labels(G,   count, labels):
    # Parsing the label element for all the details.
    label_details = []
    for label in labels:
        temp_node = {}
        temp_node.update(label.attrib)
        for more_details in label:
            temp_node.update(more_details.attrib)
        label_details.append(temp_node)
    for node in label_details:
        temp_node = {'data': {}}
        # Give an id to the label element.
        interface.add_node(G, count)
        _node_graphics(G, count, node)
        # temp_node['data']['x'] = node['CenterX']
        # temp_node['data']['y'] = node['CenterY']
        interface.add_node_x_coordinate(G, count, node['CenterX'])
        interface.add_node_y_coordinate(G, count, node['CenterY'])
        # Again not sure about this
        # temp_node['data']['content'] = node['TextLabel']
        interface.add_node_label(G, count, node['TextLabel'])
        # Again not sure about this
        interface.add_node_fontsize(G, count, node['FontSize'])
        # temp_node['data']['font_size'] = node['FontSize']
        # By default we choose white :)
        interface.add_node_color(G, count, 'white')
        # temp_node['data']['background_color'] = 'white'
        interface.add_node_background_opacity(G, count, 0)
        # temp_node['data']['background_opacity'] = 0
        # increase count, i.e. to keep unique ids for shapes, nodes, labels.
        count = count + 1
    return G,   count


def parse_interactions(G,   count, interactions):
    # Create a list of (x, y) coordinates of an edge
    # every element of the list can be either of length of 2 or 3
    # as curved edges are represented by 3 coordinates.
    edge_details = []
    for edge in interactions:
        for details in edge:
            temp_edge = []
            for more in details:
                if 'X' in more.attrib and 'Y' in more.attrib:
                    temp_edge.append((more.attrib['X'], more.attrib['Y']))
            edge_details.append(temp_edge)

    # the above way of adding attributes will append after every empty list
    # something like [['something'], [], ['more'], [], ['something']]
    # that's why we use the magic of list slicing [::2]
    # create temp edge ids
    temp_edge_ids = []
    for edge in edge_details[::2]:
        edge_id = []
        for nodes in edge:
            temp_node = {'data': {}}
            interface.add_node(G, count)
            # temp_node['data']['id'] = count
            edge_id.append(count)
            interface.add_node_x_coordinate(G, count, nodes[0])
            # temp_node['data']['x'] = nodes[0]
            interface.add_node_y_coordinate(G, count, nodes[1])
            # temp_node['data']['y'] = nodes[1]
            interface.add_node_color(G, count, 'white')
            # temp_node['data']['background_color'] = 'white'
            interface.add_node_background_opacity(G, count, 0)
            # temp_node['data']['background_opacity'] = 0
            count = count + 1
        temp_edge_ids.append(edge_id)

    # create edges
    # TODO: extract more information from edges, i.e arrow shapes
    # right now by default we are using triangle as arrow shape.
    for edge in temp_edge_ids:
        temp_edge = {'data': {}}
        if len(edge) == 2:
            interface.add_edge(G, edge[0], edge[1])
            interface.add_edge_target_arrow_shape(G, edge[0], edge[1], 'triangle')
        if len(edge) == 3:
            interface.add_edge(G, edge[0], edge[1])
            interface.add_edge_target_arrow_shape(G, edge[0], edge[1], 'triangle')

            temp_edge = {'data': {}}
            interface.add_edge(G, edge[1], edge[2])

    # This is the where magic happens, creating the layout
    # for the GPML file.
    return G, count


def set_gpml_layout(G):
    default_layout = []
    for node in G.nodes_iter(data=True):
        temp = dict()
        temp['id'] = str(node[0])
        temp['x'] = float(node[1]["x"])
        temp['y'] = float(node[1]["y"])
        default_layout.append(temp)

    # Well, we need it in JSON format. So ..
    default_layout = json.dumps(default_layout)
    return default_layout


def parse_groups(G, groups):
    for group in groups:
        temp_node = {'data': {}}
        interface.add_node(G, group.attrib['GroupId'])
        # temp_node['data']['id'] = group.attrib['GroupId']
        interface.add_node_color(G,group.attrib['GroupId'], 'white')
        # temp_node['data']['background_color'] = 'white'
        interface.add_node_border_color(G, group.attrib['GroupId'], 'black')
        # temp_node['data']['border_color'] = 'black'
    return G


def _node_graphics(G, count, node):
    if not ('CenterX' in node and 'CenterY' in node):
        return {"Error": "GPML file must contain X and Y coordinates"
                "of all the node type elements! Value for node"
                + str(node['TextLabel']) + " missing"}
    interface.add_node_x_coordinate(G, count, node['CenterX'])
    interface.add_node_y_coordinate(G, count, node['CenterY'])

    if not ('Height' in node and 'Width' in node):
        return {"Error": "GPML file must contain the height and width"
                "of all the node type elements! Value for node"
                + str(node['TextLabel']) + " missing"}
    interface.add_node_height(G, count, node['Height'])
    interface.add_node_width(G, count, node['Width'])

    if 'Align' in node:
        interface.add_node_horizontal_alignment(G, count, node['Align'], gpml=True)

    if 'Valign' in node:
        interface.add_node_vertical_alignment(G, count, node['Valign'], gpml=True)

