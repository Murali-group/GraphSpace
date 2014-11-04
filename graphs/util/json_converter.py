import json

def convert_json(original_json):
    '''
        Converts original_json that's used in Cytoscape Web
        such that it is compatible with the new Cytoscape.js

        See: http://cytoscape.github.io/cytoscape.js/

        Original json structure used for Cytoscape Web:
        {
            "metadata": {

            },

            "graph": {
                "data": {
                    "nodes": [ 
                        { "id": "node1", "label": "n1", ... },
                        { "id": "node2", "label": "n2", ... },
                        ...
                    ],
                    "edges": [ 
                        { "id": "edge1", "label": "e1", ... },
                        { "id": "edge2", "label": "e2", ... },
                        ...
                    ]
                }
            }
        }

        New json structure:
        {
            "metadata": {

            },

            "graph": {
                "nodes": [
                    {"data": {"id": "node1", "label": "n1", ...}},
                    {"data": {"id": "node2", "label": "n2", ...}},
                    ...
                ],
                "edges": [
                    {"data": {"id": "edge1", "label": "e1", ...}},
                    {"data": {"id": "edge2", "label": "e2", ...}},
                    ...
                ]
            }
        }
    '''

    #parse old json data
    old_json = json.loads(original_json)
    old_nodes = old_json['graph']['data']['nodes']
    old_edges = old_json['graph']['data']['edges']

    new_nodes, new_edges = [], []

    #format node and edge data
    for node in old_nodes:
        new_nodes.append({"data": node})

    for edge in old_edges:
        new_edges.append({"data": edge})

    #build the new json
    new_json = {}
    new_json['metadata'] = old_json['metadata']
    new_json['graph'] = {}
    new_json['graph']['nodes'] = new_nodes
    new_json['graph']['edges'] = new_edges

    return json.dumps(new_json, indent=4)
