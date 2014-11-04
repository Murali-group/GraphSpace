from db_conn import Database
import json

def populate_edge_table():
    '''
        Takes graphs stored in graph table, parse the graph
        to extract the edge data, and populate the edge table
        based on the extracted information.

        Edge table is already populated. May not need this.
    '''

    db = Database('dev2')
    conn = db.connect()

    db_session = db.new_session()


    graph = db.meta.tables['graph']
    node = db.meta.tables['node']

    #query all graph data
    graphs = db_session.query(graph.c.id, graph.c.user_id, graph.c.json).all()

    # trans = conn.begin() # open a transaction
    for g in graphs:
        # parse the graph json
        graph_json = json.loads(g[2])
        # get edges taht belong to g
        edges = graph_json['graph']['data']['edges']
        
        # i = 1
        for e in edges:
            # print 'Edge %d' % i

            head_user_id = g[1]
            head_graph_id = g[0]
            head_id = e['target']
            tail_user_id = g[1]
            tail_graph_id = g[0] 
            tail_id = e['source']
            if 'label' in e:
                label = e['label']
            else:
                label = ''
            directed = e['directed']
            # print head_user_id, head_graph_id, head_id, tail_user_id, tail_graph_id, tail_id, label, directed
            # print db_session.query(node.c.id, node.c.label, node.c.user_id, node.c.graph_id).filter(node.c.id == head_id, node.c.user_id == head_user_id, node.c.graph_id == head_graph_id).one()
            # print '-----------------'
            
            try:
                insert = "insert into edge values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                    head_user_id, head_graph_id, head_id, tail_user_id, tail_graph_id, tail_id, label, directed)
                conn.execute(insert)
            except:
                raise
        #     i = i + 1
        # i = 1

        break

    # commit the transaction    
    try:
        trans.commit()
    except:
        trans.rollback()
        raise

    # close the connection
    db.close()

if __name__ == "__main__":
    populate_edge_table()