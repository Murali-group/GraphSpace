import json


def parse_gpml(graph_json, title):
    parse_json = {"graph": {"edges": [], "nodes": []}, "metadata": {}}
    # Use xml parser to parse the GPML file
    import xml.etree.ElementTree as ET
    tree = ET.fromstring(graph_json)
    # The current GPML format
    GPML = '{http://pathvisio.org/GPML/2013a}'
    # Keep the overall count of nodes and create unique ids for
    # datanodes, shape, labels.
    # IMPORTANT!!!
    count = 0

    # Parsing the GPML file for Shape elements
    shapes = tree.findall(GPML+'Shape')
    parse_json, count = parse_shapes(parse_json, count, shapes)
    # Find all the DataNodes in the GPML file which is used to draw various
    # the various nodes of the graph
    datanodes = tree.findall(GPML+'DataNode')
    parse_json, count = parse_datanodes(parse_json, count, datanodes)
    # Parsing the GPML file for Shape elements
    labels = tree.findall(GPML+'Label')
    parse_json, count = parse_labels(parse_json, count, labels)
    # This is a crude version of getting interactions (edges) working
    # Look for all the interactions
    interactions = tree.findall(GPML+'Interaction')
    parse_json, count = parse_interactions(parse_json, count, interactions)

    layout = set_gpml_layout(parse_json)

    # To add nodes to the group we parse through the group
    # elements of the GPML file.
    groups = tree.findall(GPML+'Group')
    parse_json = parse_groups(parse_json, groups)
    parse_json['metadata']['name'] = tree.attrib['Name'] or "GPML"

    # No tags or description since CYJS doesn't give me any
    parse_json['metadata']['tags'] = []
    parse_json['metadata']['description'] = ""
    title = title or parse_json['metadata']['name']
    return parse_json, layout, title


def parse_shapes(parse_json, count, shapes):
    # Create a list of details of all the shape
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
        temp_node['data']['id'] = count
        if not ('CenterX' in node and 'CenterY' in node):
            return {"Error": "GPML file must contain X and Y coordinates"
                    "of all the shape elements!"}
        temp_node['data']['x'] = node['CenterX']
        temp_node['data']['y'] = node['CenterY']

        # Shape element may or may not contain a TextLabel field
        if 'TextLabel' in node:
            temp_node['data']['content'] = node['TextLabel']

        # Deal with the ShapeType field of the shape element,
        # improve this, make it more general, too many hacks right now.
        if 'ShapeType' in node:
            shape_type = node['ShapeType'].lower()
            if shape_type == 'brace':
                temp_node['data']['shape'] = 'rectangle'
            else:
                # oval in GPML is ellipse in cytoscape JSON
                if shape_type == 'oval':
                    temp_node['data']['shape'] = 'ellipse'
                # roundedrectangle in GPML is roundrectangle in cytoscape JSON
                elif shape_type == 'roundedrectangle':
                    temp_node['data']['shape'] = 'roundrectangle'
                # everything else works right now, may break with more testing
                else:
                    temp_node['data']['shape'] = shape_type
        else:
            # if no ShapeType given use rectangle by default.
            temp_node['data']['shape'] = 'rectangle'
        if not ('Height' in node and 'Width' in node):
            return {"Error": "GPML file must contain the height and width"
                    "of all the shape elements!"}
        temp_node['data']['height'] = node['Height']
        temp_node['data']['width'] = node['Width']
        # this is the twist out here, if you compare this with node color
        # attribute, we use the color given for border_color rather than
        # color (i.e. text color)
        if 'Color' in node:
            temp_node['data']['border_color'] = '#' + node['Color']
        if 'FillColor' in node:
            temp_node['data']['background_color'] = '#' + node['FillColor']
        else:
            temp_node['data']['background_color'] = 'white'
        # this has to be zero because we'll have multiple elements
        temp_node['data']['background_opacity'] = 0
        if 'key' in node:
            if node['key'] == 'org.pathvisio.DoubleLineProperty':
                temp_node['data']['border_style'] = 'double'
        if 'LineThickness' in node:
            temp_node['data']['border_width'] = node['LineThickness']
        else:
            temp_node['data']['border_width'] = 1
        # increase count, i.e. to keep unique ids for shapes, nodes, labels.
        count = count + 1
        parse_json['graph']['nodes'].append(temp_node)
    return parse_json, count


def parse_datanodes(parse_json, count, datanodes):
    # Parsing the DataNode element for all the details.
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
        temp_node['data']['id'] = count
        if not ('CenterX' in node and 'CenterY' in node):
            print "mri"
            return {"Error": "GPML file must contain X and Y coordinates of all the DataNode elements!"}
        temp_node['data']['x'] = node['CenterX']
        temp_node['data']['y'] = node['CenterY']
        # Not sure about text label. Haven't got an error yet for textlable
        # YET!!
        temp_node['data']['content'] = node['TextLabel']

        if not ('Height' in node and 'Width' in node):
            return {"Error": "GPML file must contain the height and width"
                    "of all the DataNode elements!"}
        temp_node['data']['height'] = node['Height']
        temp_node['data']['width'] = node['Width']
        # Again not sure about font size
        temp_node['data']['font_size'] = node['FontSize']

        if 'Color' in node:
            temp_node['data']['color'] = '#' + node['Color']
            temp_node['data']['border_color'] = '#' + node['Color']
        temp_node['data']['background_color'] = 'white'
        temp_node['data']['background_opacity'] = 0

        temp_node['data']['border_width'] = 2
        # rectangle is the default shape for all the datanodes
        temp_node['data']['shape'] = 'rectangle'
        # We use compound nodes to represent GPML groups in GraphSpace.
        if 'GroupRef' in node:
            temp_node['data']['group'] = node['GroupRef']
            temp_node['data']['parent'] = node['GroupRef']

        # increase count, i.e. to keep unique ids for shapes, nodes, labels.
        count = count + 1
        parse_json['graph']['nodes'].append(temp_node)
    return parse_json, count


def parse_labels(parse_json, count, labels):
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
        temp_node['data']['id'] = count
        if not ('CenterX' in node and 'CenterY' in node):
            return {"Error": "GPML file must contain X and Y coordinates"
                    "of all the label elements!"}
        temp_node['data']['x'] = node['CenterX']
        temp_node['data']['y'] = node['CenterY']
        # Again not sure about this
        temp_node['data']['content'] = node['TextLabel']

        if not ('Height' in node and 'Width' in node):
            return {"Error": "GPML file must contain the height and width"
                    "of all the label elements!"}
        temp_node['data']['height'] = node['Height']
        temp_node['data']['width'] = node['Width']
        # Again not sure about this
        temp_node['data']['font_size'] = node['FontSize']
        # By default we choose white :)
        temp_node['data']['background_color'] = 'white'
        temp_node['data']['background_opacity'] = 0
        # increase count, i.e. to keep unique ids for shapes, nodes, labels.
        count = count + 1
        parse_json['graph']['nodes'].append(temp_node)
    return parse_json, count


def parse_interactions(parse_json, count, interactions):
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
            temp_node['data']['id'] = count
            edge_id.append(count)
            temp_node['data']['x'] = nodes[0]
            temp_node['data']['y'] = nodes[1]
            temp_node['data']['background_color'] = 'white'
            temp_node['data']['background_opacity'] = 0
            count = count + 1
            parse_json['graph']['nodes'].append(temp_node)
        temp_edge_ids.append(edge_id)

    # create edges
    # TODO: extract more information from edges, i.e arrow shapes
    # right now by default we are using triangle as arrow shape.
    for edge in temp_edge_ids:
        temp_edge = {'data': {}}
        if len(edge) == 2:
            temp_edge['data']['source'] = edge[0]
            temp_edge['data']['target'] = edge[1]
            temp_edge['data']['target_arrow_shape'] = 'triangle'
            parse_json['graph']['edges'].append(temp_edge)
        if len(edge) == 3:
            temp_edge['data']['source'] = edge[0]
            temp_edge['data']['target'] = edge[1]
            temp_edge['data']['target_arrow_shape'] = 'triangle'
            parse_json['graph']['edges'].append(temp_edge)
            temp_edge = {'data': {}}
            temp_edge['data']['source'] = edge[1]
            temp_edge['data']['target'] = edge[2]
            parse_json['graph']['edges'].append(temp_edge)
    # This is the where magic happens, creating the layout
    # for the GPML file.
    return parse_json, count


def set_gpml_layout(parse_json):
    default_layout = []
    for node in parse_json['graph']['nodes']:
        temp = dict()
        temp['id'] = str(node["data"]["id"])
        temp['x'] = float(node["data"]["x"])
        temp['y'] = float(node["data"]["y"])
        default_layout.append(temp)

    # Well, we need it in JSON format. So ..
    default_layout = json.dumps(default_layout)
    return default_layout


def parse_groups(parse_json, groups):
    for group in groups:
        temp_node = {'data': {}}
        temp_node['data']['id'] = group.attrib['GroupId']
        temp_node['data']['background_color'] = 'white'
        temp_node['data']['border_color'] = 'black'
        parse_json['graph']['nodes'].append(temp_node)
    return parse_json
