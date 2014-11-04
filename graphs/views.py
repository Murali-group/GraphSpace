from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic

from graphs.util.db_conn import Database
from graphs.util.paginator import pager
from graphs.util.search import search
from graphs.auth.login import login
from graphs.util.db import sendForgotEmail,retrieveResetInfo, updateInfo, insert_graph, user_exists, get_graph, delete_graph, get_all_graphs, create_group, groups_for_user, remove_user_from_group, get_all_groups, get_group_by_id, remove_group, add_user_to_group, share_with_group, unshare_with_group, get_shared_graphs, get_all_groups_for_this_graph, saveLayout, getLayout, getLayouts, get_graph_info, get_public_graph_info, get_all_graph_info

from forms import LoginForm, SearchForm, RegisterForm

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_

import sqlalchemy, sqlalchemy.orm
import models
import json
import graphs.util.db_init as db_init
import bcrypt

from graphs.util.json_converter import convert_json

#get database
db = db_init.db

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
    return render(request, 'graphs/index.html', context)

def view_graph(request, uid, gid):
    '''
        View a graph with Cytoscape Web.

        @param uid - owner of the graph to view
        @param gid - graph id of the graph to view
    '''
    
    #create a new db session
    db_session = db.new_session()

    # context contains all the elements we want to render on the web
    # page. we fill in the various elements of context before calling
    # the render() function.
    #handle login
    context = login(request)

    try:
        graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    except NoResultFound:
        print uid, gid
        raise Http404

    layout_to_view = None

    if (len(request.GET.get('layout', '')) > 0):
        layout_to_view = json.dumps({"json": getLayout(request.GET.get('layout'), gid, uid)}) 
    else:
        layout_to_view = json.dumps(None)
       
    context['layout_to_view'] = layout_to_view
    context['layout_urls'] = "http://localhost:8000/graphs/" + uid + "/" + gid + "/?layout="
    
    #query[0] points to actual graph data
    # for Cytoscape.js
    context['graph'] = convert_json(graph_to_view[0]) 
    # for Cytoscape Web
    # context['graph'] = graph_to_view[0]

    shared_groups = get_all_groups_for_this_graph(graph_to_view[2])


    context['draw_graph'] = True

    json_data = json.loads(context['graph'])
    #add sidebar information to the context for display
    context['description'] = json_data['metadata']['description']

    # id of the owner of this graph
    context['owner'] = uid

    if graph_to_view[1] == 1:
        context['shared'] = 'Publicly Shared'
    else:
        context['shared'] = 'Privately Shared'

    context['shared_groups'] = shared_groups

    # graph id
    context['graph_id'] = gid

    layouts = getLayouts(uid, gid)
    context['layouts'] = layouts

    # search the graph, if performed
    search(request, context, json_data, db)

    # redirect if the user wishes to view the json data
    if request.method == "GET" and 'view_json' in request.GET:
        print redirect
        return HttpResponseRedirect("/json/%s/%s" % (uid, gid))

    return render(request, 'graphs/view_graph.html', context)

def view_json(request, uid, gid):
    '''
        View json structure of a graph.
    '''
    print 'view json'
    #create a new db session
    db_session = db.new_session()

    context = {}

    try:
        graph_to_view = db_session.query(graph.c.json).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    except NoResultFound:
        print uid, gid
        return HttpResponseNotFound('<h1>Graph not found</h1>')

    json_data = convert_json(graph_to_view[0])
    
    # add json to the context
    context['json'] = json_data

    # id of the owner of this graph
    context['owner'] = uid

    # graph id
    context['graph_id'] = gid


    return render(request, 'graphs/view_json.html', context)

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
    db_session = db.new_session()
    
    #context of the view to be passed in for rendering
    context = {}
    graph_list = None

    #handle login
    context = login(request)

    #check for authentication
    uid = request.session['uid']
    if uid is not None:
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


            graph_list =  get_shared_graphs(uid, request.GET.get('tags'))
        elif view_type == 'public':
            graph_list = get_public_graph_info(request.GET.get('tags'))
        elif view_type == 'all':
            graph_list = get_all_graph_info(request.GET.get('tags'))
        # show the graphs owned by the logged in user ("My Graphs")
        else:
            graph_list = get_graph_info(uid, request.GET.get('tags'))

        #add the list to context
        if len(graph_list) != 0:
            context['graph_list'] = graph_list
        else:
            context['graph_list'] = []

    #show public graphs if there is no logged in user
    else:
        graph_list = get_public_graph_info(request.GET.get('tags'))
        context['graph_list'] = graph_list

    if len(graph_list) == 0:
        context['graph_list'] = None

    # if context['search_result'] == True:
    #     return redirect('/result/' + context['search_word'])
        # return search_result(request, context)

    context['search_form'] = SearchForm(placeholder='Search...')

    if request.method =='GET' and 'search' in request.GET:
        # add the search word to request.GET to have it retrievable from another view.
        return HttpResponseRedirect('/result/?search=%s' % request.GET.get('search'))

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

def public_groups(request):
    ''' 
        Render the Public Groups page, showing all groups that are public. 

        This page may be removed as this page serves no purpose.
    '''

    return _groups_page(request, 'public')

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
    db_session = db.new_session()
    
    #context of the view to be passed in for rendering
    context = {}
    group_list = None

    #handle login
    context = login(request)

    #check for authentication
    uid = request.session['uid']
    if uid is not None:
        if view_type == 'member':
            #List the groups uid is a member of.
            #TODO: fix the query to display 'member of' list of groups
            # currently displays public groups
            group_list = db_session.query(group.c.group_id, group.c.name, 
                    group.c.owner_id, group.c.public
                    ).limit(20).all()
        # TODO: what is the meaning of a public group? Should we do away with this concept?
        elif view_type == 'public':
            group_list = db_session.query(group.c.group_id, group.c.name, 
                    group.c.owner_id, group.c.public
                    ).filter(group.c.public == 1).all()
        elif view_type == 'all':
            # uid must be an admin to be able to see this page.
            group_list = db_session.query(group.c.group_id, group.c.name, 
                    group.c.owner_id, group.c.public).all()
        #groups of logged in user(my groups)
        else:
            # List all groups that uid either owns or is a member of and also public groups.
            group_list = db_session.query(group.c.group_id, group.c.name, 
                    group.c.owner_id, group.c.public
                    ).filter(group.c.owner_id == uid).all()

        #add the group list to context to display on the page.
        if len(group_list) != 0:
            context['group_list'] = group_list
        else:
            context['group_list'] = None

    #show public groups if there is no logged in user
    # what to show if Public Groups page is removed?
    else:
        print 'not logged in, displaying public groups'
        group_list = db_session.query(group.c.group_id, 
                group.c.name, group.c.owner_id, group.c.public
                ).filter(group.c.public == 1).all()
        context['group_list'] = group_list

    pager_context = pager(request, group_list)

    #context['login_form'] = login_form
    if type(pager_context) is dict:
        context.update(pager_context)

    return render(request, 'graphs/groups.html', context)

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

    # pass the group_id to the context for display
    context['group_id'] = group_id

    #create a new db session
    db_session = db.new_session()

    # add search form
    search_form = SearchForm()
    context['search_form'] = search_form


    # if the group name is not one of the designated names, display graphs
    # that belong to the group
    if group_id != 'all' or group_id != 'member' or group_id != 'public':
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

        group_information = get_group_by_id(group_id)

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

    #handle login from register page.
    # context = login(request)

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

def search_result(request):
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
        # search_word = request.GET.get('search').upper()
        search_word = request.GET.get('search')
        # add the search_word to the context
        context['search_word'] = search_word
        # notify renderer to display search results via context
        context['search_result'] = True

        # create new session
        db_session = db.new_session()

        # get tables to query from
        node = db.meta.tables['node']
        edge = db.meta.tables['edge']

        # searching for edges
        if ':' in search_word:
            search_nodes = search_word.split(':')
            head_node = search_nodes[1]
            tail_node = search_nodes[0]

            print head_node
            print tail_node

            # see if node names provided are labels of nodes
            head_node_ids = db_session.query(node.c.node_id).filter(node.c.label == head_node).limit(1)
            tail_node_ids = db_session.query(node.c.node_id).filter(node.c.label == tail_node).limit(1)

            # print 'head_node_ids:', head_node_ids
            # print 'tail_node_ids:', tail_node_ids

            try:
                # filter nodes that have node id equal to node label
                set(head_node_ids).remove(head_node)
                set(tail_node_ids).remove(tail_node) 
            except:
                head_node_ids = set(head_node_ids)
                tail_node_ids = set(tail_node_ids)

            # remove duplicate entries
            head_node_ids = list(head_node_ids)
            tail_node_ids = list(tail_node_ids)

            # print 'head_node_ids:', head_node_ids
            # print 'tail_node_ids:', tail_node_ids

            # query for edges
            if len(head_node_ids) != 0 and len(tail_node_ids) != 0:
                # query for edges with matching head and tail node.
                result = db_session.query(edge.c.head_graph_id, edge.c.head_user_id, 
                                edge.c.head_id, edge.c.label).filter(
                                edge.c.head_id == head_node_ids[0][0], 
                                edge.c.tail_id == tail_node_ids[0][0]).all()
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
            result = db_session.query(node.c.graph_id, node.c.user_id,
                        node.c.node_id, node.c.label).filter(
                        or_(node.c.node_id.like("%" + search_word + "%"), 
                        node.c.label.like("%" + search_word + "%"))).all()
            # notify renderer to display edge results
            context['nodes'] = True

        if len(result) != 0:
            context['search_result'] = True
            # context['graph_list'] contains graphs to list
            # set it as result
            context['graph_list'] = result
        else:
            context['search_result'] = False
            context['graph_list'] = None

    else:
        print 'not searching'
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

    return render(request, 'graphs/result.html', context)

def logout(request):
    '''
        Log the user out and display logout page.
    '''
    context = {}
    print 'logging out'
    
    try:
        print 'delete uid'
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
    # context = forgot_password(request)
    # print context
    # return HttpResponseRedirect('/index/')

    emailId = sendForgotEmail(request.POST['forgot_email'])

    if emailId == None:
        return HttpResponse(json.dumps({"Error": "Email does not exist!"}), content_type="application/json");

    return HttpResponse(json.dumps({"Success": "Email has been sent!"}), content_type="application/json");

def reset(request):
    '''
        Allow user to reset their password
    '''
    id = request.GET.get('id')
    email = retrieveResetInfo(id)

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

    status = updateInfo(request.POST['user_id'] , hashed_pw)

    if status == None:
        return HttpResponse(json.dumps({"Error": "Email not found!"}), content_type="application/json");

    return HttpResponse("Password Updated!")

def save_layout(request, uid, gid):
    return HttpResponse(saveLayout(request.POST['layout_id'], request.POST['layout_name'], uid, gid, uid, request.POST['points'], request.POST['public'], request.POST['unlisted']))

def download(request):
    if request.POST:
        if request.POST['image']:
            response =  HttpResponse(request.POST['image'], content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="foo.png"'
            return response

##### END VIEWS #####

###### TEST VIEWS #####
def cyto(request):
    '''cytoscape web test page'''
    query = s.query(graph.c.json).filter(graph.c.user_id=='ategge@vt.edu').all()
    
    result = []
    for q in query:
        result.append(q)
    context = {'query':result[4][0]}
    #context = {}
    return render(request, 'graphs/cyto.html', context)

#test graphs page as class based view
# class GraphsView(generic.ListView):
#     template_name = 'graphs/graphs.html'
#     context_object_name = 'context'

#     def get_queryset(self):
#         return s.query(graph.c.graph_id, graph.c.modified, 
#                     graph.c.user_id, graph.c.public
#                     ).filter(graph.c.public == 1).limit(20).all()

#     def get_context_data(self, **kwargs):
#         context = login(self.request)
#         uid = self.request.session['uid']
#         if uid is not None:
#             if view_type == 'shared':
#                 #how are shared graphs indicated in the database?
#                 #show public graphs for now.
#                 graph_list = s.query(graph.c.graph_id, graph.c.modified, 
#                         graph.c.user_id, graph.c.public
#                         ).filter(graph.c.public == 1).limit(20).all()
#             elif view_type == 'public':
#                 graph_list = s.query(graph.c.graph_id, graph.c.modified, 
#                         graph.c.user_id, graph.c.public
#                         ).filter(graph.c.public == 1).all()
#             elif view_type == 'all':
#                 graph_list = s.query(graph.c.graph_id, graph.c.modified, 
#                         graph.c.user_id, graph.c.public).all()
#             #graphs of logged in user(my graphs)
#             else:
#                 graph_list = s.query(graph.c.graph_id, graph.c.modified, 
#                         graph.c.user_id, graph.c.public
#                         ).filter(graph.c.user_id == uid).all()

#             #add the list to context
#             if len(graph_list) != 0:
#                 context['graph_list'] = graph_list
#             else:
#                 context['graph_list'] = None

#             form = LoginForm(request.POST)
#         #show public graphs if there is no logged in user
#         else:
#             print 'not logged in, displaying public graphs'
#             form = LoginForm()
#             graph_list = s.query(graph.c.graph_id, 
#                     graph.c.modified, graph.c.user_id, graph.c.public
#                     ).filter(graph.c.public == 1).all()
#             context['graph_list'] = graph_list

#         pager_context = pager(self.request, graph_list)

#         context['form'] = form
#         if type(pager_context) is dict:
#             context.update(pager_context)

#         return context
##### END TEST VIEW #####

##### REST API #####
def upload_graph(request, user_id, graphname):

    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        graph_exists = insert_graph(user_id, graphname, request.FILES['graphname'].read())
        if graph_exists != None:
            return HttpResponse("Graph with " + graphname + " exists under " + user_id)
        else:
            return HttpResponse("Graph inserted into GraphSpace!")

def retrieve_graph(request, user_id, graphname):

    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        jsonData = get_graph(user_id, graphname)
        if jsonData != None:
            return HttpResponse(jsonData)
        else:
            return HttpResponse("Graph not found!")

def remove_graph(request, user_id, graphname):
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")
  
        jsonData = get_graph(user_id, graphname)
        if jsonData != None:
            delete_graph(user_id, graphname)
            return HttpResponse("Successfully deleted " + graphname + " owned by " + user_id)
        else:
            return HttpResponse("No such graph exists!")

def view_all_graphs(request, user_id):
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if user_exists(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = get_all_graphs(user_id)
        return HttpResponse(json.dumps({"Graphs": data}), content_type="application/json");


def get_groups(request):
    if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = get_all_groups()

        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");

#too much work, come back later
def get_group(request, groupname):
    if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = get_group_by_id(groupname)

        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");


def delete_group(request, groupname):
    if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = remove_group(request.POST['username'], groupname)

        return HttpResponse(json.dumps({"Response": data}), content_type="application/json");


def add_group(request, groupname):
    if request.method == 'POST':


        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group_created = create_group(request.POST['username'], groupname)
        
        if group_created != None:
            return HttpResponse("Group created")

        else:
            return HttpResponse("Group already exists!")

def get_group_for_user(request, user_id):
    if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group = groups_for_user(user_id)
        return HttpResponse(json.dumps({"User": user_id, "Groups": group}), content_type="application/json");

def add_user(request, groupname, user_id):
    if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = add_user_to_group(user_id, request.POST['username'], groupname)

        if data == None:
            return  HttpResponse(json.dumps({"Response": "Group doesn't exist!"}), content_type="application/json");

        return HttpResponse(json.dumps({"Response": data}), content_type="application/json");


def remove_user(request, groupname, user_id):
    if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group = remove_user_from_group(user_id, request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Response": group}), content_type="application/json");

def share_graph(request, graphname, groupname):
     if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        print graphname
        print groupname
        result = share_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json");

def unshare_graph(request, graphname, groupname):
     if request.method == 'POST':

        if user_exists(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        result = unshare_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json");