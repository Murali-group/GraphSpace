# Searching Graphs

The search interface in [GraphSpace](http://graphspace.org) allows a user to search for networks that have a specific attribute or tag and contain one or more nodes using [simple syntax](#query-semantics). When the user visits a matching network, GraphSpace [highlights](/Viewing_Graphs.html#highlighted-graph-elements) the nodes that match the search term. An identical search interface on the page for an individual network enables the user to refine the query. This interface also enables the user to search for specific edges within the network. [GraphSpace](http://graphspace.org) allows the user to record the URL to the network with the search terms, for sharing or for further study.

## Query Semantics

[GraphSpace](http://graphspace.org) supports three types of search terms:

1. a single string, e.g., ``wnt``. In this case, GraphSpace will return a network (a) if its ``name`` attribute contains the query as a substring or (b) if any node in the network has a ``name``, ``label``, or ``aliases`` attribute that contains the query as a substring.

2. two strings separated by a colon, e.g., ``name:wnt``. Here, GraphSpace will return a network if the ``data`` section of its JSON representation contains an attribute called ``name`` whose value contains ``wnt`` as a substring.

3. two strings separated by two colons, e.g., ``wnt::fzd``: This type of search term is only available when a user is searching a specific network. GraphSpace will highlight every edge that connects a node that matches ``wnt`` to a node that matches ``fzd``. This search ignores the direction of the edge.

All searches are case-insensitive. A user may specify more than one search term. When the user searches all networks, GraphSpace returns only those networks that match all the search terms. When the user is visualizing an individual network and searching within it, GraphSpace highlights nodes and edges that match any search term

## Searching within Multiple Graphs

The user can search for search for networks that have a specific attribute or tag and contain one or more nodes using [simple syntax](query-semantics) on [Graphs Page](http://www.graphspace.org/graphs/) by following the given steps:

1. Enter the name of the graph/node or specific network attribute mapping you are searching for in the search bar.
2. Press `Enter` key or click on the `Search` button.

In this example, the user searches for the list for graphs that contain the protein (node) `CTNNB1` (the symbol for β-catenin, a transcriptional regulator in the Wnt signaling pathway). The reduced list of graphs are the graphs where protein (node) ``name``, ``label`` or ``aliases`` contain `CTNNB1` as a substring. The match is case-insenstive. In the following example, There are six graphs owned by the user and thirty-two public graphs that contain this protein. Each link in the `Graph Name` column will take the user to a specific graph with the search term [highlighted](/Viewing_Graphs.html#highlighted-graph-elements). In this example, the user clicks on the graph with the name `KEGG-Wnt-signaling-pathway` and reaches the graph for the Wnt pathway with the searched node highlighted.

![Searching within Multiple Graphs](_static/gifs/gs-screenshot-user1-searching-withing-multiple-graphs-with-caption.gif)

## Searching within a Single Graph

The user can search for node or edges within a given graph on [GraphSpace](http://www.graphspace.org/) by following the given steps:

1. Enter the name of the node or an edge you are searching for in the search bar.
2. The nodes or edges are highlighted automatically as you type in the name of the node or edge in the search bar.


In the following example, the user searches for the graph for two proteins (nodes) `CTNNB1` and `WNT` using the query `ctnnb1, wnt`. This search query [highlights](/Viewing_Graphs.html#highlighted-graph-elements) the proteins where protein (node) ``name``, ``label`` or ``aliases`` contains `CTNNB1` or `WNT` as a substring (case-insensitive). In the following example, the graph contains four nodes which match the given query.

![Searching nodes within a Single Graph](_static/gifs/gs-screenshot-user1-searching-nodes-within-a-single-graphs-with-caption.gif)


In the following example, the user searches the graph for edges from `Wnt` to `Fzd` using the query `Wnt::Fzd`. GraphSpace
[highlights](/Viewing_Graphs.html#highlighted-graph-elements) any edge whose tail node matches ``wnt`` and whose head node matches ``fzd``. In the following example, the graph contains three edges which match the given query.

![Searching edges within a Single Graph](_static/gifs/gs-screenshot-user1-searching-edges-within-a-single-graphs-with-caption.gif)


