# Uploading Graphs

[GraphSpace](http://graphspace.org) networks follow the JavaScript Object Notation (JSON) format supported by Cytoscape.js. GraphSpace allows a user to upload a network in three different ways:

1. Users may create their own [JSON files](GraphSpace_Network_Model.html) and upload networks one-by one via the [web interface](#upload-page) at http://graphspace.org/upload.

2. Cytoscape users may export their visually-coded networks from Cytoscape and [import them directly into GraphSpace](Uploading_Graphs.html#style-file). This functionality works as follows. Since v3.1, Cytoscape has supported export of the structure of networks into JSON files and the visual elements of networks in JSON-based style files. GraphSpace can import [both these types of files](GraphSpace_Network_Model.html) at http://graphspace.org/upload. Moreover, users can import a Cytoscape style file when they are [editing the layout](Editing_Layouts.html) of a network in GraphSpace. In the future, we intend to develop a Cytoscape app to make the integration between the two systems seamless.

3. A comprehensive [RESTful API](Programmers_Guide.html#graphspace-rest-api) and a [Python module](Programmers_Guide.html#graphspace-python) called “graphspace_python” facilitate bulk uploads of networks. Both the API and the module are easy to integrate into software pipelines. Please refer to the [Programmer's Guide](Programmers_Guide.html) for more information.

## Upload Page

[GraphSpace](http://graphspace.org) provides a [simple web interface](#upload-graph-form) for uploading individual graphs. Once the graph has been uploaded, GraphSpace will provide a unique URL through which the user may interact with the graph represented by the uploaded graph files.

If a user has an account and is logged in, [this interface](#upload-graph-form) will upload the graph directly into the user's account, much like using the REST API. If a user does not have an account or is not logged in, this upload functionality will provide a unique URL through which the user may interact with the graph represented by the uploaded file. **Note: After 30 days, we will delete all graphs that are uploaded for unregistered users of GraphSpace.**


### Upload Graph Form

![Upload Graph](_static/images/upload-page/gs-screenshot-upload-graph-form.png)

The upload graph form has three input fields:

#### Graph Name 

The name of the graph. [GraphSpace](http://graphspace.org) allows users to search graphs by their name. It is a required field. The maximum allowed length of the name is 256 characters.

#### Network File 

The network file containing the graphs structure and data information in [CYJS Format](GraphSpace_Network_Model.html#cyjs-format). It is a required field.

#### Style File 

The network file containing the graphs style information in [Stylesheet JSON Format](GraphSpace_Network_Model.html#stylesheet-json-format). It is a optional field. If left empty, GraphSpace will use [default style](#default-graph-style) for displaying the graphs.

##### Default Graph Style

[GraphSpace](http://graphspace.org) uses following default style for all graphs. The default style values are used when:

- The user does not upload a [style file](#style-file) for the graph.
    OR
- The user uploads the style file which doesn't overrides the default style values.

```
[
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
            'line-style': 'solid',
            'line-color': 'black'
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'shape': 'ellipse',
            'background-color': 'yellow',
            'border-color': '#888',
            'text-halign': 'center',
            'text-valign': 'center'
        }
    }
]
```

