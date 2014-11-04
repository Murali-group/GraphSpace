import json
from time import strftime, gmtime

def upload(graph, db):
    '''
        Upload the given graph json data to the database.

        - Graph data to graph table
        - Nodes data to node table
        - Edges data to edge table

    '''

    # establish database connection
    conn = db.connect()

    # create new database session
    db_session = db.new_session()

    graph_table = db.meta.table['graph']
    node_table = db.meta.table['node']
    edge_table = db.meta.table['edge']

    current_time = strftime("%m-%d-%Y %H:%m:%S GMT", gmtime())

    # parse the graph data into python object
    json_data = json.loads(graph)

    nodes = json_data['graph']['nodes']
    edges = json_data['graph']['edges']

    # insert into appropriate tables
    # insert nodes
    for node in nodes:
        data = node['data']
        insert_node = node_table.insert().values(node_id=data['id'],
                                   label=data['label'],
                                   user_id='replace with user_id',
                                   graph_id='replace with graph_id')
        # execute insert statement
        conn.execute(insert_node)

    # insert edges
    for edge in edges:
        data = edge['data']
        insert_edge = edge_table.insert().values(head_user_id='head_user_id',
                                   head_graph_id='head_graph_id',
                                   head_id=data['target'],
                                   tail_user_id='tail_user_id',
                                   tail_graph_id='tail_graph_id',
                                   tail_id=data['source'],
                                   label=data['label'],
                                   directed=data['directed'])
        # execute insert statement
        conn.execute(insert_edge)

    # insert the graph itself to graph table
    insert_graph = graph_table.insert().values(graph_id='id',
                                    user_id='user_id',
                                    json=graph,
                                    created=current_time,
                                    modified=current_time,
                                    public=0,
                                    unlisted=0)
