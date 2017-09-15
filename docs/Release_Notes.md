# Release Notes

## [GraphSpace 2.0](https://github.com/Murali-group/GraphSpace/releases/tag/v2.0)

### Highlights

- We have added features in the layout editor that allow a user to select nodes and edges based
on color and shape in order to edit their visual properties. This functionality is available in
conjunction with the features that allowed a user to arrange the positions of the nodes in a
variety of shapes.
- We have brought the JSON format accepted by GraphSpace in line with Cytoscape.js (this JSON format is also compatible with Cytoscape).
    - We separate the structure of the network (nodes and edges) from the description of the visual styles of the nodes and edges.
    - Cytoscape.js supports a network-level ``data`` section in the JSON file specifying the network structure. We allow users to include network-specific attributes in this section, e.g., ``PMID``, ``authors``, and ``organism``.
    - Cytoscape.js supports a ``data`` section within each node. Currently, GraphSpace recognizes an attribute called \aliases" in this section, through which the network creator can specify a list of aliases for the node.
    - GraphSpace now supports CSS-based Cytoscape.js JSON files for specifying the style of the graph. GraphSpace users can import these files either in the ``Upload`` section or the ``Layout Editor`` section.
    - We have deprecated support for the JSON format supported only by GraphSpace.
- We have streamlined the search interface and made it more efficient. We have added support to search for networks that match a specific attribute (key-value pair) in addition to nodes. The search also includes the \aliases" attribute of nodes. We have disabled support for ``Exact`` searches: GraphSpace now supports only case-insensitive and substring searches.
- Concomitant with these changes, we now allow Cytoscape users to export their visually-coded networks from Cytoscape and to import them directly into GraphSpace.
- We have added support to allow a group owner to invite another person to a group via a signup link.
- To facilitate bulk uploads of networks to GraphSpace, we have implemented the Graphspace python module that a user can install from PyPI.



## [GraphSpace 1.1](https://github.com/Murali-group/GraphSpace/releases/tag/v1.1)

### Bug Fixes
- Fixed bug reported when trying to use the Forgot Password functionality.

## [GraphSpace 1.0](https://github.com/Murali-group/GraphSpace/releases/tag/v1.0)

### Highlights
- This is the first public release of GraphSpace.
