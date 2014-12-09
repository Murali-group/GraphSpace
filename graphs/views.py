from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic

from graphs.util.db_conn import Database
from graphs.util.paginator import pager
from graphs.util.search import search, find_element
from graphs.util import db
from graphs.auth.login import login
from forms import LoginForm, SearchForm, RegisterForm

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_, and_

import sqlalchemy, sqlalchemy.orm
import models
import json
import graphs.util.db_init as db_init
import bcrypt

from graphs.util.json_converter import convert_json

#get database
data_connection = db_init.db

#get tables from the database
graph = db_init.graph
user = db_init.user
group = db_init.group
group_to_graph = db_init.group_to_graph

##### VIEWS #####
def index(request):
    '''Render the main page'''

    # handle login.
    # see graphs.auth.login for details
    context = login(request)

    if context['Error'] != None:
        return HttpResponse(json.dumps({"Error": context['Error']}), content_type="application/json");

    if request.session['uid'] != None:
        return _graphs_page(request, 'my graphs')
    return render(request, 'graphs/index.html', context)

def view_graph(request, uid, gid):
    '''
        View a graph with Cytoscape Web.

        @param uid - owner of the graph to view
        @param gid - graph id of the graph to view
    '''
    #create a new db session
    db_session = data_connection.new_session()

    # context contains all the elements we want to render on the web
    # page. we fill in the various elements of context before calling
    # the render() function.
    #handle login
    context = login(request)

    try:

        if db.is_public_graph(uid, gid):
            graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
        else:
            if request.session['uid'] == None:
                return HttpResponse("Not Authorized to view this!")
        
            user_is_member = None
            graph_in_groups = db.get_all_groups_for_this_graph(gid)
            for group in graph_in_groups:
                members = db.get_group_members(group)
                if request.session['uid'] in members:
                    user_is_member = True

            if db.is_admin(request.session['uid']) == 1 or request.session['uid'] == uid or user_is_member == True:
                graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
            else:
                return HttpResponse("Not Authorized to view this!")

    except NoResultFound:
        print uid, gid
        return HttpResponse("You are not Authorized to view this!")

    layout_to_view = None

    if (len(request.GET.get('layout', '')) > 0):
        if request.GET.get('layout') != 'default_breadthfirst' and request.GET.get('layout') != 'default_concentric' and request.GET.get('layout') != 'default_circle' and request.GET.get('layout') != 'default_cose' and request.GET.get('layout') != 'default_cola' and request.GET.get('layout') != 'default_arbor' and request.GET.get('layout') != 'default_springy':
            layout_to_view = json.dumps({"json": db.getLayout(request.GET.get('layout'), gid, uid)}) 
        else: 
            layout_to_view = json.dumps(None)
    else:
        layout_to_view = json.dumps(None)

    context['layout_to_view'] = layout_to_view
    context['layout_urls'] = "http://localhost:8000/graphs/" + uid + "/" + gid + "/?layout="
    
    # for Cytoscape.js
    context['graph'] = convert_json(graph_to_view[0]) 

    shared_groups = db.get_all_groups_for_this_graph(graph_to_view[2])

    context['draw_graph'] = True

    json_data = json.loads(context['graph'])

    #add sidebar information to the context for display
    if 'description' in json_data['metadata']:
        context['description'] = json_data['metadata']['description']
    else:
        context['description'] = ""

    # id of the owner of this graph
    context['owner'] = uid

    if graph_to_view[1] == 1:
        context['shared'] = 'Publicly Shared'
    else:
        context['shared'] = 'Privately Shared'

    context['shared_groups'] = shared_groups

    # graph id
    context['graph_id'] = gid

    layouts = db.getLayouts(uid, gid)
    context['layouts'] = layouts

    # search the graph, if performed
    search(request, context, json_data, data_connection)

    # redirect if the user wishes to view the json data
    if request.method == "GET" and 'view_json' in request.GET:
        return HttpResponseRedirect("/json/%s/%s" % (uid, gid))

    return render(request, 'graphs/view_graph.html', context)

def view_json(request, uid, gid):
    '''
        View json structure of a graph.
    '''
    #create a new db session
    db_session = data_connection.new_session()

    context = {}

    try:
        graph_to_view = db_session.query(graph.c.json).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    except NoResultFound:
        print uid, gid
        return HttpResponse('<h1>Graph not found</h1>')

    json_data = convert_json(graph_to_view[0])
    
    # add json to the context
    context['json'] = json_data

    # id of the owner of this graph
    context['owner'] = uid

    # graph id
    context['graph_id'] = gid

    if request:
        return render(request, 'graphs/view_json.html', context)
    else:
        return HttpResponse(json_data)

def graphs(request):
    '''Render the My Graphs page'''

    return _graphs_page(request, 'my graphs')
    
def shared_graphs(request):
    '''Render the graphs/shared/ page showing all graphs that are shared with a user'''
    
    return _graphs_page(request, 'shared') 

def public_graphs(request):
    '''Render the graphs/public/ page showing all graphs that are public'''

    return _graphs_page(request, 'public')

def all_graphs(
    request):
    '''
        Render the graphs/all/ page showing all graphs.

        Admin feature
    '''

    return _graphs_page(request, 'all')

def _graphs_page(request, view_type):
    '''
        wrapper view for the following pages:
            graphs/
            graphs/shared/
            graphs/public/
            graphs/all/

        TODO: List/view contents specific to the logged in user for each
              page.
    '''
    
    #get new session from the database
    db_session = data_connection.new_session()
    
    #context of the view to be passed in for rendering
    context = {}
    graph_list = None

    #handle login
    context = login(request)

    if context['Error']:
        return HttpResponse(context['Error'])

    #check for authentication
    uid = request.session['uid']

    context['all_tags'] = db.get_all_tags(uid, view_type)
    if uid is not None:

        if 'search' in request.GET:
            context = search_result(request, view_type)

            if view_type == 'shared':
                context['base_url'] = "http://localhost:8000/graphs/shared/"
            elif view_type == 'public':
                context['base_url'] = "http://localhost:8000/graphs/public/"
            elif view_type == 'all':
                context['base_url'] = "http://localhost:8000/graphs/all/"
            else:
                context['base_url'] = "http://localhost:8000/graphs/"
            return render(request, 'graphs/graphs.html', context)

        if 'tags' in request.GET:
            context['tags'] = request.GET.get('tags')
            
        # render information for this particular user.
        if view_type == 'shared':
            #how are shared graphs indicated in the database? 
            #To find the graphs shared with uid, we need to look at multiple
            #tables: group_to_user to see which groups uid to belong
            #to, group_to_graph to see which graphs belong to these
            #groups, and (perhaps) graphs to get the details on the
            #graphs.  
            # show public graphs for now.
            # graph_list = db_session.query(graph.c.graph_id, graph.c.modified, 
            #         graph.c.user_id, graph.c.public
            #         ).all()
            context['base_url'] = "http://localhost:8000/graphs/shared/"
            graph_list =  db.get_shared_graphs(uid, request.GET.get('tags'))
        elif view_type == 'public':
            graph_list = db.get_public_graph_info(request.GET.get('tags'))
            context['base_url'] = "http://localhost:8000/graphs/public/"
        elif view_type == 'all':
            graph_list = db.get_all_graph_info(request.GET.get('tags'))
            context['base_url'] = "http://localhost:8000/graphs/all/"
        # show the graphs owned by the logged in user ("My Graphs")
        else:
            graph_list = db.get_graph_info(uid, request.GET.get('tags'))
            context['base_url'] = "http://localhost:8000/graphs/"

        if graph_list != None:
            if len(graph_list) == 0:
                graph_list = None

        context['graph_list'] = graph_list
        my_graphs = db.get_graph_info(uid, request.GET.get('tags'))
        shared_graphs = db.get_shared_graphs(uid, request.GET.get('tags'))
        public_graphs = db.get_public_graph_info(request.GET.get('tags'))

        if my_graphs != None:
            context['my_graphs'] = len(my_graphs)
        else:
            context['my_graphs'] = 0

        if shared_graphs != None:
            context['shared_graphs'] = len(shared_graphs)
        else:
            context['shared_graphs'] = 0

        if public_graphs != None:
            context['public_graphs'] = len(public_graphs)
        else:
            context['public_graphs'] = 0

    #show public graphs if there is no logged in user
    else:
        graph_list = db.get_public_graph_info(request.GET.get('tags'))
        context['graph_list'] = graph_list

        context['my_graphs'] = 0
        context['shared_graphs'] = 0
        if graph_list != None:
            context['public_graphs'] = len(graph_list)
        else:
            context['public_graphs'] = 0

    context['search_form'] = SearchForm(placeholder='Search...')

    if request.method =='GET' and 'search' in request.GET:
        context = search_result(request, view_type)
        context['base_url'] = "http://localhost:8000/graphs/public/"

    #Divide the results of the query into pages. Currently has poor performance
    #because the page processes a query (which may take long)
    #everytime the page loads. I think that this can be improved if
    #I store the query result in the session such that it doesn't
    #process the query unnecessarily.
    if context['graph_list'] != None:
        pager_context = pager(request, context['graph_list'])
        if type(pager_context) is dict:
            context.update(pager_context)



    # indicator to include css/js footer for side menu support etc.
    context['footer'] = True

    return render(request, 'graphs/graphs.html', context)

def groups(request):
    ''' Render the Owner Of page, showing groups that are owned by the user. '''
    return _groups_page(request, 'owner of')

def groups_member(request):
    ''' Render the Member Of page, showing the groups that the user belong to .'''
    return _groups_page(request, 'member')

# def public_groups(request):
#     ''' 
#         Render the Public Groups page, showing all groups that are public. 

#         This page may be removed as this page serves no purpose.
#     '''

#     return _groups_page(request, 'public')

def all_groups(request):
    ''' 
        Render the All Groups page, showing all groups in the database.

        Admin feature.
    '''
    return _groups_page(request, 'all')

def _groups_page(request, view_type):
    '''
        wrapper view for the following pages:
            groups/
            groups/member/
            groups/public/
            groups/all/

        TODO: List/view contents specific to the logged in user for each
                  page.
    '''

    #get new session from the database
    db_session = data_connection.new_session()
    
    #context of the view to be passed in for rendering
    context = {}
    group_list = None

    #handle login
    context = login(request)

    #check for authentication
    uid = request.session['uid']
    if uid is not None:
        if view_type == 'member':
            group_list = db.info_groups_for_user(uid)

        # elif view_type == 'public':
        #     group_list = db_session.query(group.c.group_id, group.c.name, 
        #             group.c.owner_id, group.c.public
        #             ).filter(group.c.public == 1).all()
        elif view_type == 'all':
            if db.is_admin(uid) == 1:
                group_list = db_session.query(group.c.group_id, group.c.name, 
                        group.c.owner_id, group.c.public).all()
            else:
                return HttpResponse("Not Authorized to see this page!")

        #groups of logged in user(my groups)
        else:
            # List all groups that uid either owns or is a member of and also public groups.
            group_list = db_session.query(group.c.group_id, group.c.description, 
                    group.c.owner_id, group.c.public
                    ).filter(group.c.owner_id == uid).all()


        print group_list

        #add the group list to context to display on the page.
        if len(group_list) != 0:
            context['group_list'] = group_list
        else:
            context['group_list'] = None

        pager_context = pager(request, group_list)

        if type(pager_context) is dict:
            context.update(pager_context)

        return render(request, 'graphs/groups.html', context)

    #show public groups if there is no logged in user
    else:
        # group_list = db_session.query(group.c.group_id, 
        #         group.c.name, group.c.owner_id, group.c.public
        #         ).filter(group.c.public == 1).all()

        # if len(group_list) == 0:
        #     context['group_list'] = None
        # else:
        #     context['group_list'] = group_list

        return HttpResponse("Need to log in to access this page!")

    

def graphs_in_group(request, group_id):
    '''
        groups/group_name page, where group_name is the name of the
        group to view the graphs that belong to the group.

        This is the view displayed when the user clicks a group listed
        on the /groups page.

        group names that are not allowed: 'all', 'member' and 'public'.
        they are preoccupied.
    '''

    #handle login
    context = login(request)

    #create a new db session
    db_session = data_connection.new_session()

    # add search form
    search_form = SearchForm()
    context['search_form'] = search_form

    # if the group name is not one of the designated names, display graphs
    # that belong to the group
    if group_id != 'all' or group_id != 'member':

        group_list = db.groups_for_user(context['uid'])

        if group_id not in group_list:
            return HttpResponse("Not allowed to see this!")

        # query for graphs that belong to this group
        graphs_of_this_group = db_session.query(group_to_graph.c.user_id, 
                                        group_to_graph.c.graph_id).filter(
                                                    group_to_graph.c.group_id==group_id
                                                    ).subquery()

        # query the graph table for specific information of each and every graph
        # that belong to the group
        graph_data = db_session.query(graph.c.graph_id, graph.c.modified, 
                                      graph.c.user_id, graph.c.public).filter(
                                            graph.c.graph_id==graphs_of_this_group.c.graph_id
                                            ).all()


        # include the graph data to the context
        if len(graph_data) != 0:
            context['graph_data'] = graph_data
        else:
            context['graph_data'] = None

        group_information = db.get_group_by_id(group_id)

        # pass the group_id to the context for display
        context['group_id'] = group_information[0][4]

        context['group_owner'] = group_information[0][2]

        context['group_description'] = group_information[0][0]

        context['group_members'] = group_information[0][1]

        #Divide the results of the query into pages. Currently has poor performance
        #because the page processes a query (which may take long)
        #everytime the page loads. I think that this can be improved if
        #I store the query result in the session such that it doesn't
        #process the query unnecessarily.
        pager_context = pager(request, graph_data)
        if type(pager_context) is dict:
            context.update(pager_context)

        # indicator to include css/js footer for side menu support etc.
        context['footer'] = True

        return render(request, 'graphs/graphs_in_group.html', context)
    # if the group name is one of the designated names, display
    # appropriate vies for each
    else:
        if group_id == 'all':
            return all_groups(request)
        elif group_id == 'member':
            return groups_member(request)
        else:
            return public_groups(request)

def help(request):
    '''
        Render the following pages:

        help/
        help/getting_started
    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_getting_started.html', context)

def help_tutorials(request):
    '''
        Render the help/tutorials page.
    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_tutorials.html', context)

def help_graphs(request):
    '''
        Render the help/graphs page.
    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_graphs.html', context)

def help_restapi(request):
    '''
        Render the help/restapi page.
    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_restapi.html', context)

def help_jsonref(request):
    '''
        Render the help/jsonref page.
    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_jsonref.html', context)

def help_about(request):
    '''
        Render the help/about page.
    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_about.html', context)

def register(request):
    '''
        Register a new user.
    '''

    #if the form has been submitted
    if request.method == 'POST' and 'user_id' in request.POST and 'password' in request.POST:
        # RegisterForm is bound to POST data
        register_form = RegisterForm(request.POST)
        # form validation
        if register_form.is_valid():
            # create new account by inserting the new account
            # record to the database
            user_id = register_form.cleaned_data['user_id']

            if user_id == None:
                return HttpResponse(json.dumps({"Error": "Email already exists!"}), content_type="application/json");
            
            # hash the password using bcrypt library
            hashed_pw = bcrypt.hashpw(
                            register_form.cleaned_data['password'], 
                            bcrypt.gensalt())
            activated = 1
            activate_code = 'activate_code'
            public = 0
            unlisted = 0
            admin = 0

            # user table is on a separate database
            db = Database('test')
            user = db.meta.tables['user']

            # build insert statement to insert the new user
            # info into the database.
            new_user = user.insert().values(user_id=user_id,
                                 password=hashed_pw,
                                 activated=activated,
                                 activate_code=activate_code,
                                 public=public,
                                 unlisted=unlisted,
                                 admin=admin)

            # make connection to the database
            conn = db.connect()
            # execute the insert statement
            # see Executing part at
            # http://docs.sqlalchemy.org/en/rel_0_9/core/tutorial.html#coretutorial-insert-expressions 
            conn.execute(new_user)
            # close connection
            db.close()

            # should display success message. not there yet.
            return HttpResponseRedirect('/index/')
    else:
        register_form = RegisterForm() # An unbound form

    context['register_form'] = register_form
    context['footer'] = True

    return render(request, 'graphs/register.html', context)

def search_result(request, view_type):
    '''
        Perform search and display search results.

        This function searches for nodes and edges stored
        in the database.
    '''

    # start building page context
    context = login(request)

    search_form = SearchForm(request.GET, placeholder='Search...')

    # make sure the submitted for is valid. 
    if search_form.is_valid():
        # retrieve the search word from url
        search_word = request.GET.get('search')
        # add the search_word to the context
        context['search_word'] = search_word
        # notify renderer to display search results via context
        context['search_result'] = True

        # create new session
        db_session = data_connection.new_session()

        # get tables to query from
        node = data_connection.meta.tables['node']
        edge = data_connection.meta.tables['edge']
        search_graph = data_connection.meta.tables['graph']
        search_group_to_graph = data_connection.meta.tables['group_to_graph']
        search_group_to_user = data_connection.meta.tables['group_to_user']

        context['my_graphs'] = []
        context['shared_graphs'] = []
        context['public_graphs'] = []

        # searching for edges
        if ':' in search_word:
            search_nodes = search_word.split(':')
            head_node = search_nodes[0]
            tail_node = search_nodes[1]

            # see if node names provided are labels of nodes
            head_node_ids = db_session.query(node.c.node_id).filter(node.c.label == head_node).limit(1)
            tail_node_ids = db_session.query(node.c.node_id).filter(node.c.label == tail_node).limit(1)

            head_node_ids = list(head_node_ids)
            tail_node_ids = list(tail_node_ids)

            # query for edges
            if len(head_node_ids) != 0 and len(tail_node_ids) != 0:

                if 'uid' in context and context['uid'] != None:
                    # query for edges with matching head and tail node.
                    public_result = db_session.query(edge.c.head_graph_id, edge.c.head_user_id, 
                                    edge.c.head_id, edge.c.label).filter(
                                    edge.c.head_id == head_node_ids[0][0], 
                                    edge.c.tail_id == tail_node_ids[0][0]).filter(edge.c.head_graph_id == search_graph.c.graph_id).filter(search_graph.c.public == 1).all()

                    for name in public_result:
                        context['public_graphs'].append(name)

                    owner_result = db_session.query(edge.c.head_graph_id, edge.c.head_user_id, 
                                    edge.c.head_id, edge.c.label).filter(
                                    edge.c.head_id == head_node_ids[0][0], 
                                    edge.c.tail_id == tail_node_ids[0][0]).filter(edge.c.head_graph_id == search_graph.c.graph_id).filter(search_graph.c.user_id == context['uid']).all()

                    for name in owner_result:
                        context['my_graphs'].append(name)

                    group_result = db_session.query(edge.c.head_graph_id, edge.c.head_user_id, 
                                    edge.c.head_id, edge.c.label).filter(
                                    edge.c.head_id == head_node_ids[0][0], 
                                    edge.c.tail_id == tail_node_ids[0][0]).filter(edge.c.head_graph_id == search_group_to_graph.c.graph_id).filter(search_group_to_graph.c.user_id == context['uid']).all()

                    for name in group_result:
                        context['shared_graphs'].append(name)

                    result = list(set(public_result + group_result + owner_result))

                else:
                    # query for edges with matching head and tail node.
                    public_result = db_session.query(edge.c.head_graph_id, edge.c.head_user_id, 
                                    edge.c.head_id, edge.c.label).filter(
                                    edge.c.head_id == head_node_ids[0][0], 
                                    edge.c.tail_id == tail_node_ids[0][0]).filter(edge.c.head_graph_id == search_graph.c.graph_id).filter(search_graph.c.public == 1).all()

                    for name in public_result:
                        context['public_graphs'].append(name)

                    context['graph_list'] = list(set(context['public_graphs']))

                    if len(context['public_graphs']) > 0:
                        context['search_result'] = True
                    else:
                        context['search_result'] = None

                    # add search form to the context
                    context['search_form'] = search_form


                    # add pagination
                    if context['graph_list'] != None and len(context['graph_list']) > 0:
                        pager_context = pager(request, context['graph_list'])

                        if type(pager_context) is dict:
                            context.update(pager_context)

                        context['public_graphs'] = len(context['graph_list'])

                    else:
                        context['graph_list'] = None
                        context['public_graphs'] = 0

                    context['footer'] = True
                    return context

            else:
                # assume the given words are ids of nodes.
                # query for the edges using given node names
                result = db_session.query(edge.c.head_graph_id, edge.c.head_user_id, 
                                edge.c.head_id, edge.c.label).filter(
                                edge.c.head_id == head_node, 
                                edge.c.tail_id == tail_node).all()

            # notify renderer to display edge results
            context['nodes'] = False
            
        # searching for nodes
        else:

            if 'uid' in context and context['uid'] != None:
                #search graph that user owns
                owner_result_name = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.node_id.like("%" + search_word + "%")).filter(node.c.graph_id == search_graph.c.graph_id).filter(search_graph.c.user_id == context['uid']).all()
                
                if owner_result_name != None:
                    for name in owner_result_name:
                        context['my_graphs'].append(name)

                owner_result_label = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.label.like("%" + search_word + "%")).filter(node.c.graph_id == search_graph.c.graph_id).filter(search_graph.c.user_id == context['uid']).all()

                if owner_result_label != None:
                    for label in owner_result_label:
                        context['my_graphs'].append(label)


                context['my_graphs'] = list(set(context['my_graphs']))

                #search graphs that are public
                public_result = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.node_id.like("%" + search_word + "%")).filter(node.c.graph_id == search_graph.c.graph_id).filter(search_graph.c.public == 1).all()
                
                public_result_label = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.label.like("%" + search_word + "%")).filter(node.c.graph_id == search_graph.c.graph_id).filter(search_graph.c.public == 1).all()

                if public_result != None:
                    for name in public_result:
                        context['public_graphs'].append(name)

                if public_result_label != None:
                    for name in public_result_label:
                        context['public_graphs'].append(name)


                context['public_graphs'] = list(set(context['public_graphs']))

                # result = list(set(owner_result_name + public_result))

                group_result = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.node_id.like("%" + search_word + "%")).filter(node.c.graph_id == search_group_to_graph.c.graph_id).filter(search_group_to_graph.c.user_id == context['uid']).all()

                group_result_label = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.label.like("%" + search_word + "%")).filter(node.c.graph_id == search_group_to_graph.c.graph_id).filter(search_group_to_graph.c.user_id == search_group_to_user.c.user_id).filter(search_group_to_user.c.user_id == context['uid']).all()

                if group_result != None:
                    for name in group_result:
                        context['shared_graphs'].append(name)

                if group_result_label != None:
                    for name in group_result_label:
                        context['shared_graphs'].append(name)

                context['shared_graphs'] = list(set(context['shared_graphs']))


                result = list(set(owner_result_name + public_result + group_result + owner_result_label + public_result_label + group_result_label))

            else:

                #search graphs that are public
                public_result = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.node_id.like("%" + search_word + "%")).filter(node.c.graph_id == search_graph.c.graph_id).filter(search_graph.c.public == 1).all()
                
                public_result_label = db_session.query(node.c.graph_id, node.c.user_id,
                            node.c.node_id, node.c.label).filter(node.c.label.like("%" + search_word + "%")).filter(node.c.graph_id == search_graph.c.graph_id).filter(search_graph.c.public == 1).all()

                if public_result != None:
                    for name in public_result:
                        context['public_graphs'].append(name)

                if public_result_label != None:
                    for name in public_result_label:
                        context['public_graphs'].append(name)

                context['graph_list'] = list(set(context['public_graphs']))

                if len(context['public_graphs']) > 0:
                    context['search_result'] = True

                    # add search form to the context
                    context['search_form'] = search_form

                    # add pagination
                    if context['graph_list'] != None:
                        pager_context = pager(request, context['graph_list'])

                        if type(pager_context) is dict:
                            context.update(pager_context)

                    context['footer'] = True
                    context['public_graphs'] = len(context['graph_list'])

                    return context

            # notify renderer to display node results
            context['nodes'] = True

        if len(result) != 0:
            context['search_result'] = True
            if view_type == 'shared':
                result = context['shared_graphs']
            elif view_type == 'public':
                result = context['public_graphs']
            else:
                result = context['my_graphs']

            context['graph_list'] = result
           
        else:
            context['search_result'] = False
            context['graph_list'] = None

    else:
        context['search_result'] = False
        # An unbound form
        search_form = SearchForm(placeholder='Search...')

    # add search form to the context
    context['search_form'] = search_form

    # add pagination
    if context['graph_list'] != None:
        pager_context = pager(request, context['graph_list'])

        if type(pager_context) is dict:
            context.update(pager_context)

    context['footer'] = True

    context['my_graphs'] = len(context['my_graphs'])
    context['shared_graphs'] = len(context['shared_graphs'])
    context['public_graphs'] = len(context['public_graphs'])

    return context

def retrieveIDs(request):

    if request.POST:
        db_session = data_connection.new_session()
        graph_to_view = db_session.query(graph.c.json).filter(graph.c.user_id==request.POST['uid'], graph.c.graph_id==request.POST['gid']).one()
        json_data =  json.loads(convert_json(graph_to_view[0]))
        return HttpResponse(find_element(request.POST['searchTerms'], request.POST['gid'], json_data, data_connection))


def logout(request):
    '''
        Log the user out and display logout page.
    '''
    context = {}
    
    try:
        del request.session['uid']
    except KeyError:
        # TODO: should something be done here?
        pass

    # redirect to the main page after logout.
    return HttpResponseRedirect('/index/')

def forgot(request):
    '''
        Email user the link to reset their password
    '''

    emailId = db.sendForgotEmail(request.POST['forgot_email'])

    if emailId == None:
        return HttpResponse(json.dumps({"Error": "Email does not exist!"}), content_type="application/json");

    return HttpResponse(json.dumps({"Success": "Email has been sent!"}), content_type="application/json");

def reset(request):
    '''
        Allow user to reset their password
    '''
    id = request.GET.get('id')
    email = db.retrieveResetInfo(id)

    if email == None:
        return HttpResponse(json.dumps({"Error": "Unrecognized ID"}), content_type="application/json");

    context = {"email": email}

    return render(request, 'graphs/reset.html', context)

def resetPassword(request):
    '''
        Reset their password
    '''
    # hash the password using bcrypt library
    hashed_pw = bcrypt.hashpw(
                    request.POST['pass'], 
                    bcrypt.gensalt())

    status = db.updateInfo(request.POST['user_id'] , hashed_pw)

    if status == None:
        return HttpResponse(json.dumps({"Error": "Email not found!"}), content_type="application/json");

    return HttpResponse("Password Updated!")

def save_layout(request, uid, gid):
    return HttpResponse(db.saveLayout(request.POST['layout_id'], request.POST['layout_name'], uid, gid, uid, request.POST['points'], request.POST['public'], request.POST['unlisted']))

def download(request):
    if request.POST:
        if request.POST['image']:
            response =  HttpResponse(request.POST['image'], content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="foo.png"'
            return response

##### END VIEWS #####

##### REST API #####
def upload_graph(request, user_id, graphname):

    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        graph_exists = db.insert_graph(user_id, graphname, request.FILES['graphname'].read())
        if graph_exists != None:
            return HttpResponse("Graph with " + graphname + " exists under " + user_id)
        else:
            return HttpResponse("Graph inserted into GraphSpace!")

def retrieve_graph(request, user_id, graphname):

    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        jsonData = db.get_graph(user_id, graphname)
        if jsonData != None:
            return HttpResponse(jsonData)
        else:
            return HttpResponse("Graph not found!")

def remove_graph(request, user_id, graphname):
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")
  
        jsonData = db.get_graph(user_id, graphname)
        if jsonData != None:
            db.delete_graph(user_id, graphname)
            return HttpResponse("Successfully deleted " + graphname + " owned by " + user_id)
        else:
            return HttpResponse("No such graph exists!")

def view_all_graphs(request, user_id):
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.get_all_graphs(user_id)
        return HttpResponse(json.dumps({"Graphs": data}), content_type="application/json");


def get_groups(request):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.get_all_groups()
        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");

#too much work, come back later
def get_group(request, groupname):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.get_group_by_id(groupname)
        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");


def delete_group(request, groupname):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.remove_group(request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Response": data}), content_type="application/json");


def add_group(request, groupname):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group_created = db.create_group(request.POST['username'], groupname)
        
        if group_created != None:
            return HttpResponse(json.dumps({"Upload": "Success", "Group Name": group_created}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"Upload": "Fail", "Error": "Group name already exists for this account"}), content_type="application/json")

def get_group_for_user(request, user_id):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group = db.groups_for_user(user_id)
        return HttpResponse(json.dumps({"User": user_id, "Groups": group}), content_type="application/json")

def add_user(request, groupname, user_id):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.add_user_to_group(user_id, request.POST['username'], groupname)

        if data == None:
            return  HttpResponse(json.dumps({"Response": "Group doesn't exist or user has already been added!"}), content_type="application/json")

        return HttpResponse(json.dumps({"Response": data}), content_type="application/json")


def remove_user(request, groupname, user_id):
    if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group = db.remove_user_from_group(user_id, request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Response": group}), content_type="application/json")

def share_graph(request, graphname, groupname):
     if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        result = db.share_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")

def unshare_graph(request, graphname, groupname):
     if request.method == 'POST':

        if db.user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        result = db.unshare_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")