from graphs.forms import *
from sqlalchemy import or_, and_

def search(request, context, json, db):
    '''
        Simple node/edge search on the JSON itself for use in 
        view_graph view.
    '''
    #if the search form has been submitted
    if request.method == 'GET' and 'search' in request.GET:
        # SearchForm is bound to GET data
        search_form = SearchForm(request.GET, placeholder='Search graph...')
        # context['search_form'] = search_form
        # form validation
        if search_form.is_valid():
            # get search word
            search_word = search_form.cleaned_data['search'].upper()

            # find_element(search_word, json)
            # # search for edge
            if ':' in search_word:
                # the user is searching for an edge
                # parse the search_word to get the head/tail nodes
                search_nodes = search_word.split(':')
                head_node = search_nodes[1]
                tail_node = search_nodes[0]

                # print 'head:', head_node
                # print 'tail:', tail_node

                # match the head node label to the 
                # corresponding node id if possible
                for node in json['graph']['nodes']:
                    print node
                    if node['data']['label'] == unicode(head_node):
                        head_node = node['data']['id']
                        print "head_node:", head_node
                        break

                # match the tail node label to the 
                # corresponding node id if possible
                for node in json['graph']['nodes']:
                    if node['data']['label'] == tail_node:
                        tail_node = node['data']['id']
                        print "tail_node:", tail_node
                        break


                # create new db session
                db_session = db.new_session()
                # get edge table
                edge = db.meta.tables['edge']

                # query for the edge searching
                result = db_session.query(edge.c.label).filter(or_(
                            and_(head_node == edge.c.head_id, tail_node == edge.c.tail_id),
                            and_(head_node == edge.c.tail_id, tail_node == edge.c.head_id))).all()

                # print 'result:', result

                # refine search result by removing duplicates
                result = list(set(result))

                # print 'result:', result
                # print 'result[0][0]:', result[0][0]
                # print 'result:', result
                result_id = None
                # find the corresponding edge id
                # there may be more than 1 result
                for r in result:
                    # match result to json data
                    for e in json['graph']['edges']:
                        if 'label' in e['data']:
                            if r[0] == e['data']['label']:
                                if 'id' in e['data']:
                                    result_id = e['data']['id']
                                    break
                                else:
                                    result_id = None # ??
                        else:
                            result_id = None
                
            # search for node
            else:
                # the user is searching for a node
                # To search for a node across different graphs, we need
                # to search Node table. 

                # match node label with node id
                ##### for Cytoscape Web #####
                # for node in json['graph']['data']['nodes']:
                #     if node['label'] == search_word:
                #         node_id = node['id']
                #         print "node_id:", node_id
                #         break
                #     else:
                #         node_id = None
                #############################

                ##### for Cytoscape.js #####
                for node in json['graph']['nodes']:
                    # search word can be a node id
                    if node['data']['id'].lower() == search_word.lower():
                        result_id = search_word
                        print "result_id:", result_id
                        break

                    # search word can be a node label
                    if node['data']['label'] == search_word:
                        result_id = node['data']['id']
                        break
                    else:
                        result_id = None
            #     ############################

            #     # For now, use Cytoscape Web API to search for a node in a graph
            #     # result_script = \
            #     #     '<script>$(document).ready(function() {window.vis.ready(function() {var n = window.vis.node("%s"); window.vis.select([n]); }); });</script>' % node_id
            #     # result_script = \
            #     #     '<script>$(document).ready(function() {window.cy.nodes("#%s").select(); });</script>' % node_id
            
            # include result in the context
            context['result_id'] = result_id
            # include search information in the context
            context['search_result'] = True
            # context['result_script'] = result_script
    else:
        print 'not searching'
        context['search_result'] = False
        search_form = SearchForm(placeholder='Search graph...') # An unbound form

    # add search form to the context
    context['search_form'] = search_form

def find_element(search_word, json, db):
    # create new db session
    db_session = db.new_session()
    
    # search for edge
    if ':' in search_word:
        # the user is searching for an edge
        # parse the search_word to get the head/tail nodes
        search_nodes = search_word.split(':')
        head_node = search_nodes[1]
        tail_node = search_nodes[0]


        # match the head node label to the 
        # corresponding node id if possible
        for node in json['graph']['nodes']:
            if node['data']['label'] == unicode(head_node):
                head_node = node['data']['id']
                break

        # match the tail node label to the 
        # corresponding node id if possible
        for node in json['graph']['nodes']:
            if node['data']['label'] == tail_node:
                tail_node = node['data']['id']
                break

        # get edge table
        edge = db.meta.tables['edge']

        # query for the edge searching
        result = db_session.query(edge.c.label).filter(or_(
                    and_(head_node == edge.c.head_id, tail_node == edge.c.tail_id),
                    and_(head_node == edge.c.tail_id, tail_node == edge.c.head_id))).all()

        # refine search result by removing duplicates
        result = list(set(result))

        result_id = None
        # find the corresponding edge id
        # there may be more than 1 result
        for r in result:
            # match result to json data
            for e in json['graph']['edges']:
                if 'label' in e['data']:
                    if r[0] in e['data']['label']:
                        print 'tesitng'
                        if 'id' in e['data']:
                            result_id = e['data']['id']
                            break
                        else:
                            result_id = None # ??
                else:
                    result_id = None
        
        print result_id
    # search for node
    else:
        # the user is searching for a node
        # To search for a node across different graphs, we need
        # to search Node table. 

        # match node label with node id
        ##### for Cytoscape Web #####
        # for node in json['graph']['data']['nodes']:
        #     if node['label'] == search_word:
        #         node_id = node['id']
        #         print "node_id:", node_id
        #         break
        #     else:
        #         node_id = None
        #############################

        ##### for Cytoscape.js #####
        for node in json['graph']['nodes']:
            # search word can be a node id
            if node['data']['id'].lower() == search_word.lower():
                result_id = search_word
                print "result_id:", result_id
                break

            # search word can be a node label
            if node['data']['label'] == search_word:
                result_id = node['data']['id']
                break
            else:
                result_id = None

    return result_id
        ############################

        # For now, use Cytoscape Web API to search for a node in a graph
        # result_script = \
        #     '<script>$(document).ready(function() {window.vis.ready(function() {var n = window.vis.node("%s"); window.vis.select([n]); }); });</script>' % node_id
        # result_script = \
        #     '<script>$(document).ready(function() {window.cy.nodes("#%s").select(); });</script>' % node_id
    