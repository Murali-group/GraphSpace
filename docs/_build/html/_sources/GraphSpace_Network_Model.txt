# GraphSpace Network Model

## CYJS Format

GraphSpace only supports one of the [Cytoscape.js supported](http://js.cytoscape.org/#notation/elements-json) JSON formats, which is:
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

This [JSON (JavaScript Object Notation)](http://www.json.org/) format is defined by Cytoscape for storing network structure and data information. A Cytoscape (v3.1 or later) user can easily [export their graph](http://manual.cytoscape.org/en/stable/Cytoscape.js_and_Cytoscape.html#export-network-and-table-to-cytoscape-js) in above mentioned JSON format. We call the format as `CYJS format` because the extension of the exportable JSON file from Cytoscape App is `.cyjs`.

**Note:** Any deviation from this format may result in GraphSpace rejecting the graph or problems in rendering the graph. 

### Elements JSON

The elements JSON object contains two types of lists:

1.  [Nodes](#node-object): An array of [node objects](#node-object) describing the nodes in the graph.
2.  [Edges](#edge-object): An array of [edge objects](#edge-object) describing the edges in the graph.

### Graph Data Attributes

The `Graph Data Attributes` object specifies name-value pair describing the graph. The `Graph Data Attributes` are mapped to the Cytoscape network table for a network on import. Cytoscape supports `Graph Data Attributes` for both import and export. Please refer to [list of graph data attributes treated specially by GraphSpace](#graph-data-attributes-attributes-treated-specially-by-graphspace) to make the best use of GraphSpace's features.
    
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
    
    Node Data Attributes specify name-value pairs describing the node. Cytoscape requires that each Node Object should have an  `id` data attribute which can uniquely identify the element in the graph. The users can define more data-attributes to describe the node. But, if the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing. Please refer to [list of node data attributes treated specially by GraphSpace](#node-data-attributes-attributes-treated-specially-by-graphspace) to make the best use of GraphSpace's features.
    
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

The `Edge Object` describes a node in the graph. An `Edge Object` typically contains a data object which is defined as following:

- **Edge Data Attributes**: 
    
    Edge Data Attributes specify name-value pairs describing the edge. Cytoscape requires that each Edge Object should have  `source` and `target` data attributes which can respectively identify the source and target nodes for the edge in the graph. The users can define more data-attributes to describe the edge. But, if the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data attributes without any processing. Please refer to [list of edge data attributes treated specially by GraphSpace](#edge-data-attributes-attributes-treated-specially-by-graphspace) to make the best use of GraphSpace's features.
    
    
### Graph Data Attributes Attributes Treated Specially by GraphSpace

- required:

    - `name` – text – Name of the graph. It is later used for searching the graph in GraphSpace.
    - `tags` – list of strings – Used to categorize graphs. See Tags for more information.
    - `description` – text – May be HTML formatted string. May be link to image hosted elsewhere. May simly be a string which contains information such as a legend or significance of the graph.
    
- optional:

    - `title` – text – Name that is displayed on top of graph while viewing it.
    
**Note:** The user can use add more data attributes to embed information about the graph. If the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing.

    
### Node Data Attributes Attributes Treated Specially by GraphSpace

- required:

    - `id` – text – A unique id representing the node.
    
- optional:

    - `label` – text – The text that is displayed inside of the node unless it is overidden by the `content` style-attribute in the [stylesheet JSON](#stylesheet-json-format).
    - `popup` - text - A string that will be displayed in a popup window when the user clicks the node. This string can be HTML-formatted.
    - `k` - integer -An integer index for this node. GraphSpace uses this attribute when the user seeks to step through the nodes and edges of the graph.
    
**Note:** The user can use add more data attributes to embed information about the node. But, if the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing.


### Edge Data Attributes Attributes Treated Specially by GraphSpace

- required:

    - `source` – text – The id of the node where the edge is coming from.
    - `target` – text – The id of the node where edge is going to.
    
- optional:

    - `popup` - text - A string that will be displayed in a popup window when the user clicks the edge. This string can be HTML-formatted.
    - `k` - integer - An integer index for this node. GraphSpace uses this attribute when the user seeks to step through the nodes and edges of the graph.
    
**Note:** The user can use add more data attributes to embed information about the edge. But, if the attributes are not specially treated by GraphSpace, they will be treated as "opaque". This means that GraphSpace will store or transmit the data without any processing.

### Sample JSON

The following example is a CYJS formatted JSON for GraphSpace.

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

