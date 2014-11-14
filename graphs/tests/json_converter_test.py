'''
    Test script for json_converter
'''
from graphs.util.json_converter import convert_json
from graphs.util.db_conn import Database

import json

#connect to database
db = Database('dev')

#get tables from database
graph = db.meta.tables['graph']

sample_json = '''
        {
            "metadata": {

            },

            "graph": {
                "data": {
                    "nodes": [ 
                        { "id": "node1", "label": "n1" },
                        { "id": "node2", "label": "n2" }
                    ],
                    "edges": [ 
                        { "id": "edge1", "label": "e1" },
                        { "id": "edge2", "label": "e2" }
                    ]
                }
            }
        }
        '''

wanted = '''
        {
            "metadata": {

            },

            "graph": {
                "nodes": [
                    {"data": {"id": "node1", "label": "n1"}},
                    {"data": {"id": "node2", "label": "n2"}}
                ],
                "edges": [
                    {"data": {"id": "edge1", "label": "e1"}},
                    {"data": {"id": "edge2", "label": "e2"}}
                ]
            }
        }
        '''

def basic_test():
    returned = convert_json(sample_json)
    # print json.loads(wanted)
    # print returned
    assert json.loads(returned) == json.loads(wanted)

def initial_test():
    '''
        Query 1 graph json from the development database and
        convert it.
    '''

    session = db.new_session()

    graph_json = session.query(graph.c.json).limit(1).all()

    processed_json = json.loads(convert_json(graph_json[0][0]))

    print json.dumps(processed_json, indent=4)

if __name__ == "__main__":
    '''
        run tests
    '''
    basic_test()
    initial_test()