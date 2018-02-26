# Viewing Graphs

When viewing a graph, you will notice several tabs above the graph. Clicking on a tab link will reveal the tab. The Graph Page has following 5 tabs:

- Graph Visualization Tab
- Graph Information Tab
- Edges Tab
- Nodes Tab
- Layouts Tab


## Graph Visualization Tab

The Graph Visualization Tab has two sections:
- Left section shows the actual graph.
- Right section shows multiple interaction options.

In this example, the graph has 325 edges and 132 nodes.

![Graph Visualization Tab](_static/images/gs-screenshot-user1-lovastatin-graph-visualization-tab.png)

### Node and Edge Popups

Each node or edge in a graph may have information embedded in it via the popup attribute. Clicking on a node or edge will [highlight](#highlighted-graph-elements) them. If the clicked node/edge contains popup attribute (see JSON reference), popup attribute's value will appear in a pop-up box; otherwise, no popup will be shown. If the popup attribute's value is formatted in HTML, GraphSpace will interpret it appropriately else it will use it as free-text information. 

The image below shows an example of the popup shown for a node JAK2. 

![Graph Visualization Tab](_static/images/gs-screenshot-user1-lovastatin-node-popup.png)

### Highlighted Graph Elements

GraphSpace highlights nodes/edges if they are selected. If selected, GraphSpace highlights the elements by adding an overlay around the elements in red color.
 

<table cellspacing="0">
<caption>The image below shows an example of node EGFR before and after highlighting.</caption>
<tr> 
   
   <td class="">
      <img src="_static/images/gs-screenshot-user1-lovastatin-node-before-highlighted-egfr.png" alt="Before Highlighted"/>
   </td>               
   <td class="">
      <img src="_static/images/gs-screenshot-user1-lovastatin-node-after-highlighted-egfr.png" alt="After Highlighted"/>
   </td> 
</tr>
<tr>                          
   <th>EGFR before highlighting </th> 
   <th>EGFR after highlighting </th>              
</tr>
</table>



## Graph Information Tab

As its name suggests, the `Graph Information` tab displays information about the entire graph, e.g., a legend of node and edge shapes and colors. The user can go to `Graph Information` tab by clicking on the `Graph Information` tab link above the graph. The information that appears in `Graph Information` tab must be included in the JSON for the graph uploaded by the user using the RESTful API.

The image below shows an example of Graph Information Tab when user clicks on the `Graph Information` tab link:

![Graph Information Tab Image](_static/images/gs-screenshot-user1-lovastatin-graph-information-tab.png)

## Edges Tab

As its name suggests, the `Edges` tab displays information about the edges in a table format. The table contains following columns:

1. **Edge Name** - Name of the edge.
2. **Tail Node** - Label of the tail node.
3. **Head Node** - Label of the head node.

The image below shows an example of Edges Tab when user clicks on the `Edges` tab link:

![Graph Edges Tab Image](_static/images/gs-screenshot-user1-lovastatin-graph-edges-tab.png)

## Nodes Tab

As its name suggests, the `Nodes` tab displays information about the nodes in a table format. The table contains following columns:

1. **Node Name** - Name of the node.
2. **Node Label** - Label for the node.

The image below shows an example of Nodes Tab when user clicks on the `Nodes` tab link:

![Graph Nodes Tab Image](_static/images/gs-screenshot-user1-lovastatin-graph-nodes-tab.png)

## Layouts Tab

As its name suggests, the `Layouts` tab displays information about the layouts in a table format. The tab contains two types of layouts:

- **Private Layouts** - The user has created them in earlier sessions by manually modifying the positions of nodes and edges. But the user has not shared them with any other user.
- **Shared Layouts** - These layouts were created by the user who has access to this graph and shared the layout with other users who have access to this graph.
    
The icons next to each layout name allow the user to (i) change its name, (ii) share/unshare it with other users who have access to this graph, (iii) delete this layout.

The image below shows an example of Layouts Tab when user clicks on the `Layouts` tab link. In this example, the user has created 1 private layout and has access to four shared layouts.

![Graph Layouts Tab Image](_static/images/gs-screenshot-user1-lovastatin-graph-layouts-tab.png)



