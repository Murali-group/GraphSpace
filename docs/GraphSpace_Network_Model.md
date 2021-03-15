# GraphSpace Network Model

[GraphSpace](http://graphspace.org) networks follow a [Cytoscape.js supported](http://js.cytoscape.org/#notation/elements-json) [JSON](http://www.json.org/) format that separates the [specification of the network structure](#cyjs-format) (nodes and edges) from the [description of the visual styles of the nodes and edges](#stylesheet-json-format) (e.g., colors, widths, shapes, labels). 

1. [CYJS Format](#cyjs-format) - Format is defined by Cytoscape.js for storing network structure and data information.
2. [Stylesheet JSON format](#stylesheet-json-format) - Format is defined by Cytoscape.js for storing the visual styles of the nodes and edges (e.g., colors, widths, shapes, labels) in CSS-based [JSON](http://www.json.org/) format.

Graph information in these formats can be exported from or imported to Cytoscape (version 3.1.1 or greater). 

## CYJS Format

[GraphSpace](http://graphspace.org) only supports one of the [Cytoscape.js supported](http://js.cytoscape.org/#notation/elements-json) [JSON](http://www.json.org/) formats for storing network structure and data information:

```
{
    "elements":{  // Elements JSON
        "nodes":[ // List of Node Objects
            {  
                "data": { // Node Data Attributes
                    "id": ...
                },
                "position": { // Node Position Attributes
                    "x": ...
                    "y": ...
                }
            }, 
            .
            .
        ],
        "edges":[ // List of Edge Objects
            {
                "data": { // Edge Data Attributes
                    "source": ..., 
                    "target": ...
                }
            }, 
            .
            .
        ]
    },
    "data": {   // Graph Data Attributes
        "title": ...,       
        "tags": [..],       
        "description": ... 
    }
}
```
A Cytoscape (v3.1 or later) user can easily [export their graph](http://manual.cytoscape.org/en/stable/Cytoscape.js_and_Cytoscape.html#export-network-and-table-to-cytoscape-js) in the above mentioned JSON format. We call the format as `CYJS format` because the extension of the exportable JSON file from Cytoscape App is `.cyjs`.

CYJS format structure consists of two core parts:
1. [Elements JSON](#elements-json) - An object specifying the list of [nodes](#node-object) and [edges](#edge-object) in the graph.
2. [Graph Data Attributes](##graph-data-attributes) - An object specifying name-value pairs describing the graph.

**Note:** Any deviation from this format may result in GraphSpace rejecting the graph or problems in rendering the graph. 

### Elements JSON

The elements JSON object contains two types of lists:

1.  [Nodes](#node-object): An array of [node objects](#node-object) describing the nodes in the graph.
2.  [Edges](#edge-object): An array of [edge objects](#edge-object) describing the edges in the graph.

### Graph Data Attributes

Cytoscape.js supports a network-level ``data`` section in the JSON file specifying name-value pairs describing the graph. In this section, GraphSpace gives users the freedom to include any attributes such as ``name``, ``title``, ``description``, and ``tags`` that best characterize the network. GraphSpace displays the ``name`` attribute to identify networks in the list that a user can access and in the list that match search results. When the user accesses a specific network, GraphSpace displays the ``title`` above the layout of the graph and the content of the ``description`` attribute in the tab called [Graph Information](/Viewing_Graphs.html#graph-information-tab). The Graph Information tab for an individual network displays all its attributes and their values.

Graph also allows the users to search for networks with specific attribute values as described [here](/Searching_Graphs.html#query-semantics). Cytoscape supports `Graph Data Attributes` for both import and export. The `Graph Data Attributes` are mapped to the Cytoscape network table for a network on import.

Please refer to the [list of graph data attributes treated specially by GraphSpace](#graph-data-attributes-attributes-treated-specially-by-graphspace) to make the best use of GraphSpace's features.
    
### Node Object

```
{
    "data": {     // Node Data Attributes
        "id": ... // unique identifier for the node
    },
    "position": { // Position Attributes
        "x": ...
        "y": ...
    }
}           
```

The `Node Object` describes a node in the graph. A `Node Object` typically contains two types of attributes:

1. **Node Data Attributes**: 
    
    Node Data Attributes specify name-value pairs describing the node. Cytoscape requires that each Node Object should have an  `id` or `name` data attribute which can uniquely identify the element in the graph. The users can define more data-attributes to describe the node. But, if the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing. Please refer to [list of node data attributes treated specially by GraphSpace](#node-data-attributes-attributes-treated-specially-by-graphspace) to make the best use of GraphSpace's features.
    
    **Note**: GraphSpace uses `id` and `name` attributes interchangeably. If both attributes are specified, we overwrite the `name` attribute with the value provided in `id` attribute.
    
2. **Position Attributes**: 
    
    Position Attributes specify the [model position](http://js.cytoscape.org/#notation/position) of the node in the graph layout. For example, `{ x: 100, y: 100 }` specifies a point 100 pixels to the right and 100 pixels down from the top-left corner of the viewport at zoom 1 and pan (0,0).
    
### Edge Object

```
{
    "data": {     // Node Data Attributes
        "source": ..., // identifier for the source node
        "target": ...  // identifier for the target node
    }
}           
```

The `Edge Object` describes an edge in the graph. An `Edge Object` typically contains a data object which is defined as following:

- **Edge Data Attributes**: 
    
    Edge Data Attributes specify name-value pairs describing the edge. Cytoscape requires that each Edge Object should have  `source` and `target` data attributes which can respectively identify the source and target nodes for the edge in the graph. The users can define more data-attributes to describe the edge. But, if the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data attributes without any processing. Please refer to [list of edge data attributes treated specially by GraphSpace](#edge-data-attributes-attributes-treated-specially-by-graphspace) to make the best use of GraphSpace's features.
    
    
### Graph Data Attributes Attributes Treated Specially by GraphSpace

[GraphSpace](http://graphspace.org) gives users the freedom to include any attributes that best characterize the network. If the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing.

- required:

    - `name` – text – Name of the graph. Refer to [query semantics](/Searching_Graphs.html#query-semantics) section to find how `name` attribute is used for [searching graphs](). The maximum allowed length of the name is 256 characters.
    - `tags` – list of strings – Used to categorize graphs. See the section on [organizing graphs using tags](/Organizing_Graphs_Using_Tags.html) for more information.
    - `description` – text – May be HTML formatted string. May be link to image hosted elsewhere. May simly be a string which contains information such as a [legend or significance of the graph](/Viewing_Graphs.html#graph-information-tab). This information is displayed in the tab called [Graph Informtaion](/Viewing_Graphs.html#graph-information-tab).
    
- optional:

    - `title` – text – Name that is [displayed above the layout of the graph](/Viewing_Graphs.html#graph-visualization-tab).
    
### Node Data Attributes Attributes Treated Specially by GraphSpace

[GraphSpace](http://graphspace.org) gives users the freedom to include any attributes that best characterize the node. If the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing.


- required:

    - `id` or `name` – text – A unique id representing the node. If both attributes are specified, we overwrite the `name` attribute with the value provided in `id` attribute.  GraphSpace uses it to [search for nodes with a matching name](/Searching_Graphs.html#query-semantics).
    
- optional:
	
    - `label` – text – The text that is displayed inside of the node unless it is overidden by the `content` style-attribute in the [stylesheet JSON](#stylesheet-json-format).  GraphSpace uses it to [search for nodes with a matching name](/Searching_Graphs.html#query-semantics).
    - `aliases` - list of strings - A list of alternative identifiers for the node. GraphSpace uses it to [search for nodes with a matching name](/Searching_Graphs.html#query-semantics).
    - `popup` - text - A string that will be displayed in a [popup window](/Viewing_Graphs.html#node-and-edge-popups) when the user clicks the node. This string can be HTML-formatted information, e.g., Gene Ontology annotations and database links for a protein; or types, mechanism, and database sources for an interaction.
    - `k` - integer - An integer-valued attribute for this node, which denotes a rank. Through this attribute, GraphSpace allows the user to [filter nodes and edges](/Interacting_with_Graphs.html#filter-nodes-and-edges) in a network visualization.

### Edge Data Attributes Attributes Treated Specially by GraphSpace

[GraphSpace](http://graphspace.org) gives users the freedom to include any attributes that best characterize the edge. If the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing.

- required:

    - `source` – text – The id of the node where the edge is coming from.
    - `target` – text – The id of the node where edge is going to.
    
- optional:

    - `popup` - text - A string that will be displayed in a [popup window](/Viewing_Graphs.html#node-and-edge-popups) when the user clicks the edge. This string can be HTML-formatted information, e.g., Gene Ontology annotations and database links for a protein; or types, mechanism, and database sources for an interaction.
    - `k` - integer - An integer-valued attribute for this edge, which denotes a rank. Through this attribute, GraphSpace allows the user to [filter nodes and edges](/Interacting_with_Graphs.html#filter-nodes-and-edges) in a network visualization.


### Sample JSON

The following example is a CYJS formatted JSON accepted by GraphSpace.

```json
{
    "elements": {
        "nodes": [ 
            {
                "data": {
                    "id":"P4314611",
                    "label": "DCC",
                    "k": 0
                }
            }, 
            {
                "data": {
                    "id":"P0810711",
                    "label": "This is an example\n of how to use new lines for the content of\n a node.",
                    "k": 0
                }
            }
        ],
        "edges": [
            {
                "data": {
                    "source": "P4314611",
                    "target": "P0810711",
                    "k": 0
                }
            }
        ]

    },
    "data": {
        "title": "Graph Name",
        "description": "Description of graph.. can also point to an image hosted elsewhere",
        "tags": [
            "tutorial"
        ]
    }
}
```


## Stylesheet JSON Format

Cytoscape and Cytoscape.js are sharing a concept called [Style](http://manual.cytoscape.org/en/stable/Cytoscape.js_and_Cytoscape.html#export-styles-to-cytoscape-js). This is a collection of mappings from data point to network property. Cytoscape can export its Styles into CSS-based Cytoscape.js JSON. 

[Style in Cytoscape.js](http://js.cytoscape.org/#style) follows CSS conventions as closely as possible. In most cases, a property has the same name and behaviour as its corresponding CSS namesake. However, the properties in CSS are not sufficient to specify the style of some parts of the graph. In that case, additional properties are introduced that are unique to Cytoscape.js. For simplicity and ease of use, [specificity rules](http://www.w3.org/TR/css3-selectors/#specificity) are completely ignored in stylesheets by Cytoscape.js. For a given style property for a given element, the last matching selector wins.

A Cytoscape (v3.1 or later) user can export all Styles into one JSON file from **File | Export | Style** and select Cytoscape.js JSON as its format.

**Note:** Cytoscape.js [does not support all of Cytoscape Network Properties](http://manual.cytoscape.org/en/stable/Cytoscape.js_and_Cytoscape.html#limitations). Those properties will be ignored or simplified when you export to JSON Style file.

### Style Properties

Please refer to CytoscapeJS documentation for [list of style properties](http://js.cytoscape.org/#style/node-body) supported by Cytoscape.js. We thank them for the excellent documentation of their framework.


### Sample JSON

```
{
    "style": [
        {
            "selector": "node[name='P4314611']",
            "style": {
                "border-color": "#888",
                "text-halign": "center",
                "text-valign": "center",
                "border-width": "2px",
                "height": "50px",
                "width": "50px",
                "shape": "ellipse",
                "background-blacken": "0.1",
                "background-color": "yellow"
            }
        },
        {
            "selector": "node[name='P0810711']",
            "style": {
                "text-halign": "center",
                "text-valign": "center",
                "text-outline-color": "#888",
                "text-outline-width": "2px",
                "border-color": "black",
                "border-width": "5px",
                "height": "150px",
                "shape": "ellipse",
                "color": "black",
                "border-style": "double",
                "text-wrap": "wrap",
                "background-blacken": "0",
                "width": "150px",
                "background-color": "red"
            }
        },
        {
            "selector": "edge[name='P4314611-P0810711']",
            "style": {
                "curve-style": "bezier",
                "line-style": "dotted",
                "width": "12px",
                "line-color": "blue",
                "source-arrow-color": "yellow",
                "target-arrow-shape": "triangle"
            }
        }
    ]
}
```

