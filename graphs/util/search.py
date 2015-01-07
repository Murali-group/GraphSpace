# from graphs.forms import *
# from sqlalchemy import or_, and_

# def search(request, context, json, db):
#     '''
#         Called when you click a graph under a search result in the graphs page
#     '''
#     #if the search form has been submitted
#     if request.method == 'GET' and 'search' in request.GET:
#         # SearchForm is bound to GET data
#         search_form = SearchForm(request.GET, placeholder='Search graph...')
#         # context['search_form'] = search_form
#         # form validation
#         if search_form.is_valid():
#             # get search word
#             search_word = search_form.cleaned_data['search'].upper()

#             result_id = find_element(search_word, None, json, db)

#             # include result in the context
#             context['result_id'] = result_id
#             # include search information in the context
#             context['search_result'] = True
#     else:
#         print 'not searching'
#         context['search_result'] = False
#         search_form = SearchForm(placeholder='Search graph...') # An unbound form

#     # add search form to the context
#     context['search_form'] = search_form


# def find_element(search_word, graphname, json, db):
#     '''
#         Finds an element (node or edge) for a specific graph
#     '''
#     # create new db session
#     db_session = db.new_session()

#     node = db.meta.tables['node']
#     edge = db.meta.tables['edge']

#     # search for edge
#     if ':' in search_word:
#         # the user is searching for an edge
#         # parse the search_word to get the head/tail nodes
#         search_nodes = search_word.split(':')

#         #extract individual node
#         head_node = search_nodes[0]
#         tail_node = search_nodes[1]

#         head_id = ""
#         tail_id = ""

#         # match the head node label to the 
#         # corresponding node id if possible
#         for node1 in json['graph']['nodes']:
#             if node1['data']['label'] == head_node:
#                 head_id = node1['data']['id']
#                 break

#         # match the tail node label to the 
#         # corresponding node id if possible
#         for node1 in json['graph']['nodes']:
#             if node1['data']['label'] == tail_node:
#                 tail_id = node1['data']['id']
#                 break

#         if graphname != None:
#             # get edge table
#             result = db.session.query(edge.c.label).filter(and_(head_id == edge.c.head_id, tail_id == edge.c.tail_id, graphname == edge.c.head_graph_id)).all()

#             head_id = db_session.query(node.c.node_id).filter(node.c.label == head_node).filter(graphname == node.c.graph_id).all()
#             tail_id = db_session.query(node.c.node_id).filter(node.c.label == tail_node).filter(graphname == node.c.graph_id).all()
#         else:
#             # get edge table
#             result = db.session.query(edge.c.label).filter(and_(head_id == edge.c.head_id, tail_id == edge.c.tail_id)).all()

#             head_id = db_session.query(node.c.node_id).filter(node.c.label == head_node).all()
#             tail_id = db_session.query(node.c.node_id).filter(node.c.label == tail_node).all()

#         result_id = None
#         # find the corresponding edge id
#         # there may be more than 1 result
#         for r in result:
#             # match result to json data
#             for e in json['graph']['edges']:
#                 # print e
#                 if 'label' in e['data']:
#                     print r[0], tail_node + '-' + head_node, e['data']['label']
#                     if r[0] in e['data']['label'] or head_node + '-' + tail_node in e['data']['label']:
#                         if 'id' in e['data']:
#                             result_id = e['data']['id']
#                             break
#                         else:
#                             result_id = None # ??
#                 else:
#                     result_id = result[0]
        
#         return result_id
#     # search for node
#     else:
#         # the user is searching for a node
#         # To search for a node across different graphs, we need
#         # to search Node table. 
#         node_to_view_label = db_session.query(node.c.node_id).filter(node.c.label==search_word).filter(node.c.graph_id==graphname).all()
#         if node_to_view_label != None and len(node_to_view_label) > 0:
#             return node_to_view_label[0]
#         else:
#             node_to_view_name = db_session.query(node.c.node_id).filter(node.c.node_id==search_word).all()
#             if node_to_view_name != None and len(node_to_view_name) > 0:
#                 return node_to_view_name[0]
#         return None


