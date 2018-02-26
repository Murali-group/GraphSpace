# Quick Tour of Cytoscape

## Welcome Screen

The [welcome page](http://graphspace.org) greets a user when the user visits GraphSpace. The Welcome Screen is designed to access commonly used features of GraphSpace like:

- Log In
- Create Account
- Upload a graph
- List of uploaded graphs.

### Log In

The user can log-in to [GraphSpace](http://www.graphspace.org) by following the given steps:

1. Click on the `Log In` button on the top navigation bar. This will trigger a log-in window/pop-up to be displayed.
2. Enter your email address. 
3. Enter you password.
4. Click on `Submit` button to log in with the given email address.
5. If you have forgotten you password, click on the `Forgot Password` link.

![Log In](_static/gifs/gs-screenshot-user1-logging-in-with-caption.gif)

### Create Account

The user can create an account on [GraphSpace](http://www.graphspace.org) by following the given steps:

1. Click on the `Create Account` button on the top navigation bar. This will trigger a create account window/pop-up to be displayed.
2. Enter the your email address. 
3. Enter a password for your account.
4. Verify your password by entering the same password again.
5. Click on `Submit` button to create the account with the given email address and password.

![Create Account](_static/gifs/gs-screenshot-user5-creating-account-with-caption.gif)

### Upload a graph

The user can upload a graph on [GraphSpace](http://www.graphspace.org) by following the given steps:

1. Go to the [Upload Graph Page](http://www.graphspace.org/upload) by clicking on the `Upload Graph` button on [Home Page](http://www.graphspace.org/).
2. Enter a unique name for the new graph.
3. Select a CYJS file which contains the graph information.
4. Select a JSON file which contains the style information for the graph. (Optional Step)
5. Click on `Submit` button to upload the graph using the selected files.
6. Once the graph has been uploaded, [GraphSpace](http://www.graphspace.org) will provide a unique URL through which the user may interact with the graph represented by the uploaded files.

![Upload a graph](_static/gifs/gs-screenshot-user1-upload-graph-with-caption.gif)

### List of uploaded graphs

The user can go to [a page that lists the graphs](http://www.graphspace.org/graphs/) accessible by the user on [GraphSpace](http://www.graphspace.org) by following the given steps:

- Click on the button titled `Graphs` on the top navigation bar.
 
     OR

- Click on the `My Graphs` button on the [Home Page](http://www.graphspace.org/).

In this example, the user owns 33 graphs, can access 64 public graphs and 33 graphs are shared with this user.
![List of uploaded graphs](_static/gifs/gs-screenshot-user1-go-graphs-list-page-with-caption.gif)

## Searching within Multiple Graphs

The user can search for graph with a given name or node or an edge on [Graphs Page](http://www.graphspace.org/graphs/) by following the given steps:

1. Enter the name of the graph, node or an edge you are searching for in the search bar.
2. Press `Enter` key or click on the `Search` button.

In this example, the user searches for the list for graphs that contain the protein (node) `CTNNB1` (the symbol for β-catenin, a transcriptional regulator in the Wnt signaling pathway). The reduced list of graphs are the graphs where proteins names/labels (nodes) contain `CTNNB1` as a substring. In the following example, There are six graphs owned by the user and thirty-two public graphs that contain this protein. Each link in the `Graph Name` column will take the user to a specific graph with the search term highlighted. In this example, the user clicks on the graph with the name `KEGG-Wnt-signaling-pathway` and reaches the graph for the Wnt pathway with the searched node highlighted.

![Searching within Multiple Graphs](_static/gifs/gs-screenshot-user1-searching-withing-multiple-graphs-with-caption.gif)

## Searching within a Single Graph

The user can search for node or edges within a given graph on [GraphSpace](http://www.graphspace.org/) by following the given steps:

1. Enter the name of the node or an edge you are searching for in the search bar.
2. The nodes or edges are highlighted automatically as you type in the name of the node or edge in the search bar.


In the following example, the user searches for the graph for two proteins (nodes) `CTNNB1` and `WNT` using the query `ctnnb1, wnt`. This search query highlights the proteins where protein (node) name/label contains `CTNNB1` or `WNT` as a substring (case-insensitive). In the following example, the graph contains four nodes which match the given query.

![Searching nodes within a Single Graph](_static/gifs/gs-screenshot-user1-searching-nodes-within-a-single-graphs-with-caption.gif)



In the following example, the user searches for the graph for edges from `Wnt` to `Fzd` using the query `Wnt:Fzd`. This search query highlights any protein-protien interaction (edge) where tail node name or label contains `Wnt` as a substring and head node name or label contains `Fzd` as a substring. In the following example, the graph contains three edges which match the given query.

![Searching edges within a Single Graph](_static/gifs/gs-screenshot-user1-searching-edges-within-a-single-graphs-with-caption.gif)

## Interacting with a Graph

The Graph Page is designed to access features like:

- Graph Information
- Edge and Node Information
- Export Graph
- Change Layout
- Share Layout

### Graph Information

As its name suggests, the `Graph Information` panel displays information about the entire graph, e.g., a legend of node and edge shapes and colors. The user can go to `Graph Information` panel by clicking on the `Graph Information` link above the graph. The information that appears in `Graph Information` panel must be included in the JSON for the graph uploaded by the user using the RESTful API.

![Graph Details](_static/gifs/gs-screenshot-user1-graph-information-with-caption.gif)


### Edge and Node Information

Clicking on a node or edge pops up a panel with information on that node or edge. The information that appears in the pop-up panels must be included in the JSON for the graph uploaded by the user using the RESTful API.

![Edge and Node Information](_static/gifs/gs-screenshot-user1-node-edge-pop-up-with-caption.gif)

### Export Graph

[GraphSpace](http://www.graphspace.org) allows users to export a graph as an image file or a JSON file. GraphSpace does not support any other export formats since it relies on [Cytoscape.js](http://js.cytoscape.org) for this functionality, which implements only export to PNG, JPG and JSON format. 

In the following example, the user is exporting the graph as an image in PNG format.

![Export Graph](_static/gifs/gs-screenshot-user1-export-graph-png-with-caption.gif)

### Change Layout

[GraphSpace](http://www.graphspace.org) allows users to change layout using the following steps:

1. Click on the `Change Layout` button to view available layout options.
2. The `Change Layout` panel provides two alternatives:
    - **Select Layout Algorithm** - List of layout algorithms supported by GraphSpace through its use of [Cytoscape.js](http://js.cytoscape.org).
    - **Select Saved Layout** - List of layout saved by the user using GraphSpace. The user has created them in earlier sessions by manually modifying the positions of nodes and edges created by some automatic layout algorithm and saving the layout.
3. Click on a layout option to change the current layout.

In the following example, the user selects to view the layout titled "manual-top-to-bottom".
    
![Change Layout](_static/gifs/gs-screenshot-user1-change-layout-with-caption.gif)

### Share Layout

[GraphSpace](http://www.graphspace.org) allows users to share a layout using the following steps:

1. Click on the `Layouts` link above the graph.
2. The layouts panel shows two types of layouts:
    - **Private Layouts** - The user has created them in earlier sessions by manually modifying the positions of nodes and edges. But the user has not shared them with any other user.
    - **Shared Layouts** - These layouts were created by the user who has access to this graph and shared the layout with other users who have access to this graph.
    
3. Click on the `Share` link next to the layout name of a private layout you want to share with other users who have access to this graph.

Note: The icons next to each layout name allow the user to (i) change its name, (ii) share it with other users who have access to this graph, (iii) delete this layout.

![Share Layout](_static/gifs/gs-screenshot-user1-share-layout-with-caption.gif)
