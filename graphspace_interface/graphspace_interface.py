#!/usr/bin/python

## GraphSpace Interface
## Divit Singh, Anna Ritz, Allison Tegge, and T. M. Murali
## Contact: T. M. Murali (murali@cs.vt.edu)
## License: GPL version 3
##
## GraphSpace programmer's guide on the Help page: 
## http://graphspace.org/help/programmers/
##
## This python  module contains  functions for  two types  of actions.
## First, a user can add Cytoscape.js attributes to a NetworkX Graph or DiGraph object  (the nodes and edges within
## it)  that are  required for  rendering in  GraphSpace.  Note that this interface currently doesn't support multi-graphs (graphs with mulitple edges for the same (source,target) node pair.  Second,  the
## module implements  functions that call  the REST API for  posting a
## graph, deleting  a graph, and sharing  a graph with a  group. These
## functions support  a subset of the  allowed Cytoscape.js attributes
## and the REST API calls.
##
## The main() method  contains two examples of  creating, posting, and
## sharing graphs.  TODO: these should be moved to their own help page
## as illustrative examples.  This module  should not contain a main()
## method.


## Import Statements
import sys
import os
import subprocess
import re
import urllib
import json
from optparse import OptionParser
import networkx as nx
from networkx.readwrite import json_graph
import random

## global variables
#URL='http://localhost:8000'
URL='graphspace.org'

#####################################################################
## GLOBAL VARIABLES #################################################
## These lists must be updated  and maintained by the one of the
## current GraphSpace  implementers, since  GraphSpace may be  using a
## version of Cytoscape.js  that is older than the  current version in
## release. Hence,  the Cytoscape.js  website cited above  may support
## shapes  and styles  that the  version used  by GraphSpace  does not
## support.
##
## Last updated July 15, 2015. See the specified urls for details about
## these values. 

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

## See http://js.cytoscape.org/#style/edge-arrow
ALLOWED_ARROW_SHAPES = ['tee', 'triangle', 'triangle-tee', 'triangle-backcurve', 
                        'square', 'circle', 'diamond', 'none']

## See http://js.cytoscape.org/#style/edge-line
ALLOWED_EDGE_STYLES = ['solid', 'dotted', 'dashed']

ALLOWED_ARROW_FILL = ['filled', 'hollow']

## Default Metadata Dictionary. All Metadata dictionaries
## must contain these three keys. If a user-specified dictionary
## is missing a key, the default value is added.
DEFAULT_METADATA = {'description':'','tags':[],'title':''}


## END GLOBAL VARIABLES #############################################

## JSON VALIDATOR FUNCTIONS #########################################

def validate_json(G):
    """
    Validates JSON to see if all properties are consistent with API.

    @param G: NetworkX object.
    """

    # Validate all node properties
    validate_node_properties(G)

    # Validate all edge properties
    validate_edge_properties(G)

def validate_edge_properties(G):
    """
    Validates all edge properties.

    :param G: NetworkX object.
    """

    # Go through all edges to verify if edges contain valid properties
    # recognized by CytoscapeJS
    for edge_id in G.edge:

        # If edge is directed, it must have a target_arrow_shape
        if "directed" in G.edge[edge_id] and G.edge[edge_id] == "true":
            if "target_arrow_shape" not in G.edge[edge_id]:
                print "Edge: ", edge_id, "must have a target_arrow_shape property if directed is true"

        if "source_arrow_shape" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "source_arrow_shape", G.edge[edge_id]["source_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "mid_source_arrow_shape" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "mid_source_arrow_shape", G.edge[edge_id]["mid_source_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "target_arrow_shape" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "target_arrow_shape", G.edge[edge_id]["target_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "mid_target_arrow_shape" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "mid_target_arrow_shape", G.edge[edge_id]["mid_target_arrow_shape"], ALLOWED_ARROW_SHAPES)

        if "line_style" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "line_style", G.edge[edge_id]["line_style"], ALLOWED_EDGE_STYLES)

        if "source_arrow_fill" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "source_arrow_fill", G.edge[edge_id]["source_arrow_fill"], ALLOWED_ARROW_FILL)

        if "mid_source_arrow_fill" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "mid_source_arrow_fill", G.edge[edge_id]["mid_source_arrow_fill"], ALLOWED_ARROW_FILL)

        if "target_arrow_fill" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "target_arrow_fill", G.edge[edge_id]["target_arrow_fill"], ALLOWED_ARROW_FILL)

        if "mid_target_arrow_fill" in G.edge[edge_id]:
            find_property_in_array("Edge", edge_id, "mid_target_arrow_fill", G.edge[edge_id]["mid_target_arrow_fill"], ALLOWED_ARROW_FILL)

def validate_node_properties(G):
    """
    Validates all node properties.

    :param G: NetworkX object.
    """
    # Go through all nodes to verify if the nodes contain valid properties
    # recognized by CytoscapeJS
    for node_id in G.node:
        node_data = G.node[node_id]

        node_id = node_id.replace("\n", "")

        # Checks shape of nodes to make sure it contains only legal shapes
        if "shape" in node_data:
            find_property_in_array("Node", node_id, "shape", node_data["shape"], ALLOWED_NODE_SHAPES)

        # If node contains a border-style property, check to make sure it is 
        # a legal value
        if "border_style" in node_data:
            find_property_in_array("Node", node_id, "border_style", node_data["border_style"], ALLOWED_NODE_BORDER_STYLES)

        # If node contains a background_black property, check to make sure
        # they have values [-1, 1]
        if "border_blacken" in node_data:
            if node_data["border_blacken"] >= -1 and node_data["border_blacken"] <= -1:
                print "Node: ", node_data, "contains illegal border_blacken value.  Must be between [-1, 1]."

        if "background_repeat" in node_data:
            find_property_in_array("Node", node_id, "background_repeat", node_data["background_repeat"], ALLOWED_NODE_BACKGROUND_REPEAT)

        if "text_transform" in node_data:
            find_property_in_array("Node", node_id, "text_transform", node_data["text_transform"], ALLOWED_NODE_TEXT_TRANSFORM)

        if "text_wrap" in node_data:
            find_property_in_array("Node", node_id, "text_wrap", node_data["text_wrap"], ALLOWED_NODE_TEXT_WRAP)

        if "text_background_shape" in node_data:
            find_property_in_array("Node", node_id, "text_background_shape", node_data["text_background_shape"], ALLOWED_NODE_SHAPES)

        if "text_halign" in node_data:
            find_property_in_array("Node", node_id, "text_halign", node_data["text_halign"], ALLOWED_TEXT_HALIGN)

        if "text_valign" in node_data:
            find_property_in_array("Node", node_id, "text_valign", node_data["text_valign"], ALLOWED_TEXT_VALIGN)

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
        raise Exception("%s with ID: \"%s\" contains illegal %s: \"%s\".  Accepted values for this property are: %s." % (elementType, key, prop, value, array))
        
####################################################################
### NODE FUNCTIONS #################################################

def add_node(G,node_id,label='',shape='ellipse',color='#FFFFFF',height=None,\
             width=None,popup=None,k=None,bubble=None,valign='center',halign='center',style="solid",border_color='#000000',border_width=1):
    """
    Adds a  node to the NetworkX object. The  parameters G (a NetworkX
    object) and node_id (a string)  are required. All other attributes
    are optional. If  some attributes are not  specified, then default
    values will be  put in place for  now; these may be  set using the
    accessor methods later.
    
    If the node with this id exists in G, it will be overwritten.

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param label: string -- text to display on node. "\n" will be interpreted as a newline. Default = empty string.
    :param shape: string -- shape of node. Default = "ellipse".
    :param color: string -- hexadecimal representation of the color (e.g., #FFFFFF) or color name. Default = white.
    :param height: int -- height of the node's body. Use None to determine height from the number of lines in the label. Default = None.
    :param width: int -- width of the node's body, or None to determine width from length of label.  Default=None.
    :param popup: string -- Information (in HTML format) to display when this node is selected in GraphSpace. Optional. 
    :param k: int -- value for filtering nodes and edges in graph. This parameter is useful for graphs generated by the Linker algorithm (http://www.ncbi.nlm.nih.gov/pubmed/23641868). Here k is the index of the first path in which a node or edge appears. Optional.
    :param bubble: string -- color of the text outline. Using this option gives a "bubble" effect; see the bubbleeffect() function. Optional.
    :param valign: string -- vertical alignment. Default = center.
    :param halign: string -- horizontal alignment. Default = center.
    :param style: string -- style of border. Default is "solid".  If Bubble is specified, then style is overwritten.
    :param border_color: string -- color of border. Default is #000000. If Bubble is specified, then style is overwritten.
    :param border_width: int -- width of border. Default is 4.  If Bubble is specified, then style is overwritten.
    """
    G.node[node_id] = {}
    add_node_label(G,node_id,label)
    add_node_shape(G,node_id,shape)
    add_node_color(G,node_id,color)
    add_node_width(G,node_id,width,label)
    add_node_height(G,node_id,width,label)
    add_node_vertical_alignment(G,node_id,valign)
    add_node_horizontal_alignment(G,node_id,halign)
    add_node_border_style(G,node_id,style)
    add_node_border_color(G,node_id,border_color)
    add_node_border_width(G,node_id,border_width)
    #G.node[node_id]['text_outline_color']='#000000'
    if popup:
        add_node_popup(G,node_id,popup)
    if k:
        add_node_k(G,node_id,k)
    
    # If bubble is specified, use the provided color,
    if bubble:
        bubble_effect(G,node_id,bubble,whitetext=False)

    ## set height and width if len(label)==0 and height/width
    ## are None (auto-resize).  Make them very small nodes.
    ## height=width=5
    if (not width or not height) and len(label)==0:
        add_node_width(G,node_id,5,label)
        add_node_height(G,node_id,5,label)


## Setter methods for nodes.    
# Divit's Note: We want to work towards supporting all the following properties: 
# http://js.cytoscape.org/#style/node-body
# If we decide to use CytoscapeJS' API, then some of these values will have to change.
# Also, we may be able to fit in a JSON verifier in here.
# The reason is that if we follow the API, this code may check to see if the values
# are supported by CytoscapeJS (e.g., shapes)
# The properties that we require for each node so far are: label, shape ,color, height, width

# Divit: Since we are making a wrapper around Cytoscapejs supported properties, how can we keep this up to 
# date with all of the properties they support?

## TODO DIVIT I am confused about the comments above regarding CytoscapeJS' API.

def add_node_label(G,node_id,label):
    '''
    Add a label "label" to a node "node_id" in graph "G".
    The label is stored under "content" in the node information.
    Also set wrap = 'wrap' so newlines are interpreted.

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param label: string -- text to display on node. "\n" will be interpreted as a newline. 
    '''
    G.node[node_id]['content'] = label
    add_node_wrap(G,node_id,'wrap')

def add_node_wrap(G,node_id,wrap):
    '''
    Adding node wrap allows the newline '\n' to be interpreted
    as a line break for node "node_id" in graph "G".

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param wrap: string denoting the type of wrap: one of "wrap" or "none". 
    :raise exception: if the wrap parameter is not one of the allowed wrap styles.
    See ALLOWED_NODE_TEXT_WRAP for more details.
    '''
    if wrap not in ALLOWED_NODE_TEXT_WRAP:
        raise Exception('"%s" is not an allowed text wrap style.' % (wrap))
    G.node[node_id]['text_wrap'] = wrap

def add_node_shape(G,node_id,shape):
    '''
    Add a shape "shape" to node "node_id" in graph "G".

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param shape: string -- shape of node. Default = "ellipse".
    :raise exception: if the shape is not one of the allowed node shapes.
    See ALLOWED_NODE_SHAPES global variable.
    '''
    if shape not in ALLOWED_NODE_SHAPES:
        raise Exception('"%s" is not an allowed shape.' % (shape))
    G.node[node_id]['shape'] = shape

def add_node_color(G,node_id,color):
    '''
    Add a background color to the node "node_id" in graph "G".
    Color can be a name (e.g., 'black') or an HTML string (e.g., #00000).

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param color: string -- hexadecimal representation of the color (e.g., #FFFFFF) or color name.
    '''
    ## TODO: rais an exception if the color is improperly formatted.
    G.node[node_id]['background_color'] = color

def add_node_height(G,node_id,height,label,height_factor=20):
    '''Sets  the node  height for  node "node_id" in  graph "G".   If the
    height is 'None', then the height of the node is determined by the
    number of newlines in the label that will be displayed.

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param height: int -- height of the node's body. Use None to determine height from the number of lines in the label.
    :param label: string -- text to display on node. "\n" will be interpreted as a newline. Use for auto-resizing when height = None.
    :param height-factor: factor to multiply the height of the label. Default is 20.
    :warning: previous versions of this function supported an "autosize" option. Since we do not implement this option any more, the user must set the height for every node.

    '''
    if height == None: # "auto-resize" height
        # take the number of lines for the label after interpreting newlines.
        labellines = label.split('\n')
        height = len(labellines)*height_factor
    G.node[node_id]['height'] = height

def add_node_width(G,node_id,width,label,width_factor=15):
    '''
    Sets the node width for node  "node_id" in graph "G". If the width
    is 'None', then the width of  the node is determined by the length
    (number of characters) in the longest  line in the label that will
    be displayed.

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param width: int -- width of the node's body, or None to determine width from length of label.
    :param label: string -- text to display on node. "\n" will be interpreted as a newline. Used for auto-resizing when width=None.
    :param width-factor: factor to multiply the width of the label. Default is 15.
    :warning: previous versions of this function supported an "autosize" option. Since we do not implement this option any more, the user must set the height for every node.

    '''
    if width == None: # "auto-resize" width
        ## take the longest width of the label after interpreting newlines.
        labellines = label.split('\n')
        width = max([len(l) for l in labellines])*width_factor
    G.node[node_id]['width'] = width

def add_node_popup(G,node_id,popup):
    '''
    Add an HTML-formatted string with information on node "node_id" in graph "G".
    When the user clicks the node in GraphSpace, this string will appear in a pop-up panel.

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param popup: string -- Information (in HTML format) to display when this node is selected in GraphSpace. 
    '''
    G.node[node_id]['popup'] = popup

def add_node_k(G,node_id,k):
    '''
    Add a value (k) to filter the node  to node "node_id" in graph "G".
    In GraphSpace, a user may adjust a slider.  For a slider value x, only nodes with k-value less than or equal to x are displayed. 

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param k: int -- value for filtering nodes in graph.
    :warning: Nodes without a k value will always be displayed. 
    :warning: This function may be overridden to pass a non-integer; in this case, k is set to the floor of the decimal value.
    '''
    G.node[node_id]['k'] = k

def bubble_effect(G,node_id,color,whitetext=False):
    '''
    Add a "bubble effect" to the node by making the 
    border color the same as the text outline color.

    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param color: string -- hexadecimal representation of the text outline color (e.g., #FFFFFF) or a color name.
    :param whitetext: Boolean -- if True, text is colored white instead of black. Default is False.
    '''
    G.node[node_id]['text_outline_color']=color
    add_node_border_color(G,node_id,color)
    # also make outline thicker and text larger
    G.node[node_id]['text_outline_width']=4
    if whitetext:
        G.node[node_id]['color']='white'

def add_node_border_width(G,node_id,width):
    '''
    Set the border width for node "node_id" in graph "G".
    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    '''
    G.node[node_id]['border_width'] = width

def add_node_border_style(G,node_id,style):
    '''
    Set the border style for node "node_id" in graph "G".
    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :raise exception: if style is not one of the allowed styles.
    '''
    G.node[node_id]['border_style'] = style

def add_node_border_color(G,node_id,color):
    '''
    Set the border color for node "node_id" in graph "G".
    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param color: string -- hexadecimal representation of the text outline color (e.g., #FFFFFF) or a color name.
    '''
    G.node[node_id]['border_color'] = color

def add_node_vertical_alignment(G,node_id,valign):
    '''
    Set the vertical alignment of label for node "node_id" in graph "G".
    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param valign: string -- alignment of text.
    '''
    G.node[node_id]['text_valign'] = valign

def add_node_horizontal_alignment(G,node_id,halign):
    '''
    Set the vertical alignment of label for node "node_id" in graph "G".
    :param G: NetworkX object.
    :param node_id: string -- unique ID of the node.
    :param halign: string -- alignment of text.
    '''
    G.node[node_id]['text_halign'] = halign
    

## Getter methods for nodes.

## Get any attribute of a node
def get_node_attribute(G,node_id,attr):
    '''
    Get a node attribute, or None if no attribute exists.
    '''
    if attr in G.node[node_id]:
        return G.node[node_id][attr]
    else:
        return None

## These node get() functions ensure that the correct attribute is called in the get_data_attribute() function.
## They mirror the node add() functions.
def get_node_label(G,node_id):
    return get_node_attribute(G,node_id,'content')
def get_node_wrap(G,node_id):
    return get_node_attribute(G,node_id,'text_wrap')
def get_node_shape(G,node_id):
    return get_node_attribute(G,node_id,'shape')
def get_node_color(G,node_id):
    return get_node_attribute(G,node_id,'background_color')
def get_node_height(G,node_id):
    return get_node_attribute(G,node_id,'height')
def get_node_width(G,node_id,):
    return get_node_attribute(G,node_id,'width')
def get_node_popup(G,node_id):
    return get_node_attribute(G,node_id,'popup')
def get_node_k(G,node_id):
    return get_node_attribute(G,node_id,'k')
def get_node_border_width(G,node_id):
     return get_node_attribute(G,node_id,'border_width')
def get_node_border_style(G,node_id):
    return get_node_attribute(G,node_id,'border_style')
def get_node_border_color(G,node_id):
    return get_node_attribute(G,node_id,'border_color')
def get_node_vertical_alignment(G,node_id):
    return get_node_attribute(G,node_id,'text_valign')
def get_node_horizontal_alignment(G,node_id):
    return get_node_attribute(G,node_id,'text_halign')

    
####################################################################
### EDGE FUNCTIONS #################################################

def add_edge(G,source,target,color='#000000',directed=False,width=1.0,popup=None,k=None,arrow_shape='triangle',edge_style='solid',arrow_fill='filled'):
    """
    Adds a edge to the NetworkX object.  ID is required; all other attributes
    are optional. If an attribute is not specified, then default values will
    be put in place for now; these may be set using the accessor methods later.

    If the edge with this id exists in G, it will be overwritten.

    :param G: NetworkX object
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param color: string -- hexadecimal representation of the color (e.g., #000000), or the color name. Default = black.
    :param directed: bool - if True, draw the edge as directed. Default = False.
    :param width: float -- width of the edge.  Default = 1.0
    :param popup: string -- Information (in HTML format) to display when this edge is selected in GraphSpace. Optional.
    :param k: int -- value for filtering nodes and edges in graph. This parameter is useful for graphs generated by the Linker algorithm (http://www.ncbi.nlm.nih.gov/pubmed/23641868). Here k is the index of the first path in which a node or edge appears. Optional.
    :param arrow_shape: string -- shape of arrow head. Default is "triangle"
    :param edge_style: string -- style of edge. Default is "solid"
    :param arrow_fill: string -- fill of arrow. Default is "filled"
    """
    if source not in G.edge:
        G.edge[source] = {}
    G.edge[source][target] = {}
    add_edge_color(G,source,target,color)
    add_edge_directionality(G,source,target,directed)
    add_edge_width(G,source,target,width)
    add_edge_target_arrow_shape(G,source,target,arrow_shape)
    add_edge_line_style(G,source,target,edge_style)
    add_edge_target_arrow_fill(G,source,target,arrow_fill)
    if popup:
        add_edge_popup(G,source,target,popup)
    if k:
        add_edge_k(G,source,target,k)

def add_edge_color(G,source,target,color):
    '''
    Add edge color to edge ("source","target") in graph "G".
    Color both the line and the target arrow; if the edge
    is undirected, then the target arrow color doesn't matter.
    If it's directed, then the arrow color will match the line color.

    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param color: string -- hexadecimal representation of the color (e.g., #000000), or the color name. 
    '''
    G.edge[source][target]['line_color'] = color
    G.edge[source][target]['target_arrow_color'] = color

def add_edge_directionality(G,source,target,directed, arrow_shape='triangle'):
    '''
    Directs the edge ("source","target") in graph "G" from "source" to "target". 
    Sets a "directed" flag as well as adds a target arrow shape.  

    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param directed: bool - if True, draw the edge as directed.
    :param arrow_shape: string -- shape of arrow. See ALLOWED_ARROW_SHAPES.
    '''
    if directed:
        G.edge[source][target]['directed'] = 'true'
        add_edge_target_arrow_shape(G,source,target,arrow_shape)
    else:
        G.edge[source][target]['directed'] = 'false'
        add_edge_target_arrow_shape(G,source,target,'none')

def add_edge_width(G,source,target,width):
    '''
    Sets the width of edge ("source","target") in graph "G".

    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param width: float -- width of the edge.  Default = 1.0
    '''
    G.edge[source][target]['width'] = width

def add_edge_popup(G,source,target,popup):
    '''
    Add an HTML-formatted string with information on edge ("source","target") in graph "G".
    When the user clicks the edge in GraphSpace, this string will appear in a pop-up panel.

    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param popup: string -- Information (in HTML format) to display when this edge is selected in GraphSpace.
    '''
    G.edge[source][target]['popup'] = popup

def add_edge_k(G,source,target,k):
    '''
    Add a value (k) to filter the edge ("source","target") in graph "G".
    In GraphSpace, a user may adjust a slider.  For a slider value x, only edges with k-value less than or equal to x are displayed. 

    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param k: int -- value for filtering nodes in graph.
    :warning: Edges without a k value will always be displayed. 
    :warning: This function may be overridden to pass a non-integer; in this case, k is set to the floor of the decimal value.
    :raise exception: if the source and target values have a larger k value than the edge.  
    '''

    ## Cytoscape.js throws a runtime error if there's an edge with a small k (e.g., 1) but the nodes have larger k's (e.g., 5).
    ## When the slider is set to 3, the edge should be displayed but the incident nodes are not.
    sourcek = get_node_k(G,source)
    targetk = get_node_k(G,target)
    if not sourcek:
        raise Exception('Attempting to add a k value %d for edge ("%s","%s"), but node "%s" does not have a k-value.' % (k,source,target,source))
    if not targetk:
        raise Exception('Attempting to add a k value %d for edge ("%s","%s"), but node "%s" does not have a k-value.' % (k,source,target,target))
    if sourcek > k:
        raise Exception('Attempting to add a k value %d for edge ("%s","%s"), but node "%s" has a larger k-value (%d).' % (k,source,target,source,sourcek))
    if targetk > k:
        raise Exception('Attempting to add a k value %d for edge ("%s","%s"), but node "%s" has a larger k-value (%d).' % (k,source,target,target,targetk))
    
    G.edge[source][target]['k'] = k

def add_edge_target_arrow_shape(G,source,target,arrow_shape):
    '''
    Assigns an arrow shape to edge ("source","target") in graph "G".

    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    '''
    G.edge[source][target]['target_arrow_shape'] = arrow_shape

def add_edge_line_style(G,source,target,style):
    '''
    Adds the edge line style to edge ("source","target") in graph "G".
   
    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param style: string -- style of line.
    '''
    G.edge[source][target]['line_style'] = style

def add_edge_target_arrow_fill(G,source,target,fill):
    '''
    Adds the arrowhead fill to edge ("source","target") in graph "G".
   
    :param G: NetworkX object.
    :param source: string -- unique ID of the source node 
    :param target: string -- unique ID of the target node
    :param fill: string -- fill of arrowhead.
    '''
    G.edge[source][target]['target_arrow_fill'] = fill

def get_edge_attribute(G,source,target,attr):
    ''' 
    Get an attribute of an edge, or None if no such attribute exists.'
    '''
    if attr in G.edge[source][target]:
        return G.edge[source][target][attr]
    else:
        return 

## These edge get() functions ensure that the correct attribute is called in the get_edge_attribute() function.
## They mirror the edge add() functions.
def get_edge_color(G,source,target):
    return get_edge_attribute(G,source,target,'line_color')
def get_edge_directionality(G,source,target):
    return get_edge_attribute(G,source,target,'directed')
def get_edge_width(G,source,target):
    return get_edge_attribute(G,source,target,'width')
def get_edge_popup(G,source,target):
    return get_edge_attribute(G,source,target,'popup')
def get_edge_k(G,source,target):
    return get_edge_attribute(G,source,target,'k')
def get_edge_target_arrow_shape(G,source,target):
    return get_edge_attribute(G,source,target,'target_arrow_shape')
def get_edge_line_style(G,source,target):
    return get_edge_attribute(G,source,target,'line_style')
def get_edge_target_arrow_fill(G,source,target):
    return get_edge_attribute(G,source,target,'target_arrow_fill')

####################################################################
### POSTING FUNCTIONS ##############################################
    
def convertNXToDict(G,metadata={}):
    """Converts a NetworkX object G to a dictionary that can be interepreted as a JSON
    object. 
 
    :param G: NetworkX object
    :param metadata: dictionary of graph metadata. This dictionary 
    should contain a 'description' (string), 'tags' (list of strings), and 'title' (string). 
    If not specified, then this dictionary is populated with defaule values.

    If this  argument is not  specified, the returned  dictionary will
    contain an empty  description and tags list.  Note that GraphSpace
    requires these metadata  attributes to be present  in every graph,
    even if they are empty.

    :returns: dictionary -- the dictionary has the following elements:
      {'metadata':{'description':<str>,'tags':<str list>,'title':<str>},
       'graph': {'nodes': <node list>, 'edges': <edge list>},
      }
    The 'nodes' and 'edges' attributes are lists of dictionaries containing
    the attributes required by GraphSpace for all nodes and all edges, respectively.

    :raises: TypeError -- metadata does not contain the required keys.
    :raises exception: If a node or edge is missing a required attribute for converting to GraphSpace.

    """

    # Instantiate dictionary that will be returned
    out = {}

    # If the metadata dictionary is empty or incomplete, then populate it with
    # default values. Note: prior to 2016-04-26, an error was thrown if a default
    # value was missing.  Now, we print each missing key.
    for metadata_key in DEFAULT_METADATA.keys():
        if metadata_key not in metadata:
            print 'Adding default value for metadata key "%s".' % (metadata_key)
            metadata[metadata_key] = DEFAULT_METADATA[metadata_key]
    ## TODO: is it "name" or "title"? I filed a bug.
    ## When we have determined this, either make "name" a key in the default 
    ## dictionary or 
    metadata['name'] = metadata['title']

    # Add metadata information
    out['metadata'] = metadata

    # Add graph information (empty nodes and edges for now)
    out['graph'] = {'nodes':[],'edges':[]} 

    # Populate nodes
    for node_id,node_attributes in G.nodes(data=True):
        ## data dictionary
        data = {'id':node_id}
        data.update(node_attributes)
        ## node consists of data dictionary
        node = {'data':data}
        ## add node to nodes list.
        out['graph']['nodes'].append(node)

    # Populate edges
    for source_id,target_id,edge_attributes in G.edges(data=True):
        ## data dictionary
        data = {'source':source_id,'target':target_id}
        data.update(edge_attributes)
        ## edge consists of data dictionary
        edge = {'data':data}
        ## add edge to edges list
        out['graph']['edges'].append(edge)

    return out

def convertNXToJSON(G,outfile,metadata=None):
    """ 
    Converts a NetworkX object to a JSON object.
    
    :param G: NetworkX object
    :param outfile: file to write JSON to.  
    :param metadata: a dictionary of metadata for the graph. Optional.
    """
    ## convert NetworkX object to a JSON-ready dictionary
    if metadata:
        graph_dict = convertNXToDict(G,metadata)
    else:
        graph_dict = convertNXToDict(G)

    ## if outfile is specified, write json to outfile.
    json.dump(graph_dict,open(outfile,'w'),indent=4)
    print '\nWrote JSON for graph to outfile %s' % (outfile)
    return

def postGraph(G,graphid,outfile,user,password,metadata=None,logfile=None):
    """
    Posts NetworkX graph with id 'graphid' to the account of the user 'user' to GraphSpace.

    :param G: NetworkX object
    :param graphid: string -- ID of GraphSpace graph
    :param outfile: string -- output file to write JSON to. 
    :param user: string -- graph owner's username
    :param password: string -- graph owner's password
    :param metadata: dictionary of metadata for graph. Optional.
    :param logfile: filename for command outputs.  Optional.
    """
    if logfile:
        logout = open(logfile,'w')
    else:
        logout = None
        
    # convert NetworkX object to a serialized_graph
    convertNXToJSON(G,outfile,metadata)

    # check to see if this graph is already in GraphSpace.
    graph_exists = False
    cmd = _constructExistsCommand(graphid,user,password)
    outstring = execute(cmd,logout)
    outstring = json.loads(outstring)
    if outstring["StatusCode"] == 200:
        # a status code of 200 indicates that a graph already exists.
        graph_exists = True

    if graph_exists:  
        #print '\nUpdating existing graph %s from user %s' % (graphid,user)
        cmd = _constructUpdateCommand(graphid,user,password,outfile)
        execute(cmd,logout)
        
    else:
        #print '\nGraph does not exist. Posting new graph %s from user %s' % (graphid,user)
        cmd = _constructPostCommand(graphid,user,password,outfile)
        execute(cmd,logout)
    
    if logout:
        print 'command output written to %s' % (logfile)
        logout.close()

def deleteGraph(graphid,user,password):
    """
    Removes a graph (denoted by graphid and user) from GraphSpace.
    :param graphid: ID of GraphSpace graph 
    :param user: graph owner's username
    :param password: graph owner's password
    """
    print '\nRemoving existing graph %s from user %s' % (graphid,user)
    cmd = _constructDeleteCommand(graphid,user,password)
    execute(cmd)
   
def shareGraph(graphid,user,password,group,group_owner=""):
    """
    Shares an existing graph with a group.
    :param graphid: ID of GraphSpace graph
    :param user: graph owner's username
    :param password: graph owner's password
    :param group: group to share graph with.
    :param group_owner: the group owner's username. Set to the user parameter by default
    """
    if group_owner == "":
        group_owner = user
    print '\nSharing existing graph %s from user %s with group %s owned by %s' % (graphid,user,group,group_owner)
    cmd = _constructShareCommand(graphid,user,password,group,group_owner)
    outstring = execute(cmd)

def makeGraphPublic(graphid,user,password):
    """
    Makes a graph publicly viewable.
    :param graphid: ID of GraphSpace graph 
    :param user: graph owner's username
    :param password: graph owner's password
    """
    print '\nMaking graph %s from user %s public' % (graphid,user)
    cmd = _constructPublicGraphCommand(graphid,user,password)
    outstring = execute(cmd)


def makeGraphPrivate(graphid,user,password):
    """
    Makes a graph privately viewable (makes it no longer public).
    :param graphid: ID of GraphSpace graph 
    :param user: graph owner's username
    :param password: graph owner's password
    """
    print '\nMaking graph %s from user %s private' % (graphid,user)
    cmd = _constructPrivateGraphCommand(graphid,user,password)
    outstring = execute(cmd)

def makeGraphsWithTagPublic(user,password,tag):
    """
    Makes all graphs with a tag publicly viewable.
    :param user: graph owner's username
    :param password: graph owner's password
    :param tag: graph tag.
    """
    print '\nMaking graphs with tag %s from user %s public' % (tag,user)
    cmd = _constructPublicTagCommand(user,password,tag)
    outstring = execute(cmd)  

def makeGraphsWithTagPrivate(user,password,tag):
    """
    Makes all graphs with a tag privately viewable (make them no longer public).
    :param user: graph owner's username
    :param password: graph owner's password
    :param tag: graph tag.
    """
    print '\nMaking graphs with tag %s from user %s public' % (tag,user)
    cmd = _constructPrivateTagCommand(user,password,tag)
    outstring = execute(cmd)  

####################################################################
### CURL COMMANDS  #################################################

## TODO: add block comments with param/return descriptions.
def _constructExistsCommand(graphid,user,password):
    cmd = 'curl -X POST %s/api/users/%s/graph/exists/%s/ -F username=%s -F password=%s ; echo' % \
          (URL,user,graphid,user,password)
    return cmd

def _constructPostCommand(graphid,user,password,outfile):
    cmd = 'curl -X POST %s/api/users/%s/graph/add/%s/ -F username=%s -F password=%s -F graphname=@%s ; echo'  % \
          (URL, user, graphid, user, password, outfile) 
    return cmd

def _constructUpdateCommand(graphid,user,password,outfile):
    cmd = 'curl -X POST %s/api/users/%s/graph/update/%s/ -F username=%s -F password=%s -F graphname=@%s ; echo'  % \
          (URL, user, graphid, user, password, outfile) 
    return cmd

def _constructDeleteCommand(graphid,user,password):
    cmd = 'curl -X POST %s/api/users/%s/graph/delete/%s/ -F username=%s -F password=%s ; echo'  % \
          (URL, user, graphid, user, password) 
    return cmd

def _constructShareCommand(graphid,user,password,groupid,group_owner):
    cmd = 'curl -X POST %s/api/users/graphs/%s/share/%s/%s/ -F username=%s -F password=%s ; echo'  % \
          (URL, graphid,group_owner,groupid,user,password)
    return cmd

def _constructPublicGraphCommand(graphid,user,password):
    cmd = 'curl -X POST %s/api/users/%s/graph/makeGraphPublic/%s/ -F username=%s -F password=%s; echo' % \
            (URL,user,graphid,user,password)
    return cmd

def _constructPrivateGraphCommand(graphid,user,password):
    cmd = 'curl -X POST %s/api/users/%s/graph/makeGraphPrivate/%s/ -F username=%s -F password=%s; echo' % \
            (URL,user,graphid,user,password)
    return cmd

def _constructPublicTagCommand(user,password,tag):
    cmd = 'curl -X POST %s/api/tags/user/%s/%s/makePublic/ -F username=%s -F password=%s; echo' % \
            (URL,user,tag,user,password)
    return cmd

def _constructPrivateTagCommand(user,password,tag):
    cmd = 'curl -X POST %s/api/tags/user/%s/%s/makePrivate/ -F username=%s -F password=%s; echo' % \
            (URL,user,tag,user,password)
    return cmd

def execute(cmd,logout=None):
    """
    Executes the command, using subprocess.Popen.  We need to capture
    the output, so we cannot simply us os.system().
    :param cmd: string -- command to execute
    :param logout: File object -- File of log output or None.
    :return out: string -- output of command
    """
    print cmd
    proc = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if logout:
        logout.write(cmd+'\n')
        logout.write(out+'\n')
    if 'ERROR' in out:
        print 'Error in output string of CURL command:'
        print out
        sys.exit()
    return out
