from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic
from django.templatetags.static import static

from graphs.util.db_conn import Database
from graphs.util.paginator import pager
from graphs.util import db
from graphs.auth.login import login
from forms import LoginForm, SearchForm, RegisterForm
from django.conf import settings

from sqlalchemy.orm.exc import NoResultFound

import sqlalchemy, sqlalchemy.orm
import models
import json
import graphs.util.db_init as db_init
import bcrypt
import os
from operator import itemgetter
from itertools import groupby
from graphs.forms import LoginForm, RegisterForm

#get database
data_connection = db_init.db

#get tables from the database
graph = db_init.graph
user = db_init.user
group = db_init.group
group_to_graph = db_init.group_to_graph

URL_PATH = settings.URL_PATH

##### VIEWS #####
def index(request):
    '''Render the main page

        :param request: HTTP GET Request
    '''

    #####################
    # UNCOMMENT THESE ON INITIAL START UP TO POPULATE TABLES
    #####################
    # db.add_everyone_to_password_reset()

    # db.insert_all_edges_from_json()
    #####################

    # UNCOMENT THIS LINE IF YOU WANT TO CONVERT JSON TO MATCH CS 2.4 PROPERTIES
    # db.update_json_to_cs_2_4()

    # handle login.
    # see graphs.auth.login for details

    if request.method == 'POST' and db.need_to_reset_password(request.POST['user_id']) != None:
        context = {}
        print 'TESTING'
        request.session['uid'] = None
        result = db.sendForgotEmail(request.POST['user_id'])
        context['Error'] = "Need to reset your password! An email has been sent to " + request.POST['user_id'] + ' with instructions to reset your password!'
        return HttpResponse(json.dumps(db.throwError(400, context['Error'])), content_type="application/json");

    context = login(request)

    if context['Error'] == None:
        # # If there is someone logged in, return the 'my graphs' page, otherwise redirect to inital screen
        # if request.session['uid'] != None:
        #     return _graphs_page(request, 'my graphs')
        return render(request, 'graphs/index.html', context)
    else:
        return HttpResponse(json.dumps(db.throwError(400, context['Error'])), content_type="application/json");

def view_graph(request, uid, gid):
    '''
        View a graph with CytoscapeJS.

        :param request: HTTP GET Request
        :param uid: Owner of the graph to view
        :param gid: Graph id of the graph to view
    '''
    #create a new db session
    db_session = data_connection.new_session()

    # context contains all the elements we want to render on the web
    # page. we fill in the various elements of context before calling
    # the render() function.
    #handle login
    context = login(request)

    # if the graph is public, or if a user is a member 
    # of the group where this graph is shared
    # or if he owns this graph, then allow him to view it
    # otherwise do not allow it
    if db.is_public_graph(uid, gid) or 'Public_User_' in uid:
        graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    elif request.session['uid'] == None:
        context['Error'] = "You are not authorized to view this graph, create an account and contact graph's owner for permission to see this graph."
        return render(request, 'graphs/error.html', context)
    else:
        # If the user is member of group where this graph is shared
        user_is_member = db.can_see_shared_graph(context['uid'], uid, gid)

        # if admin, then they can see everything
        if db.is_admin(request.session['uid']) == 1 or request.session['uid'] == uid or user_is_member == True:
            if len(db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).all()) > 0:
                graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
            else: 
                context['Error'] = "Graph: " + gid + " does not exist for " + uid + ".  Upload a graph with this name into GraphSpace in order to see it."
                return render(request, 'graphs/error.html', context)
        else:
            context['Error'] = "You are not authorized to view this graph, please contact graph's owner for permission."
            return render(request, 'graphs/error.html', context)
    # Get correct layout for the graph to view
    context = db.set_layout_context(request, context, uid, gid)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])
    context['draw_graph'] = True

    # Get all the groups that are shared for this graph
    shared_groups = db.get_all_groups_for_this_graph(uid, graph_to_view[2])

    format_shared_groups = []
    for shared_group in shared_groups:
        format_shared_groups.append((shared_group[0], shared_group[1]))

    context['shared_groups'] = format_shared_groups

    if graph_to_view[1] == 1:
        context['shared'] = 'Publicly Shared'
    else:
        context['shared'] = 'Privately Shared'

    # TODO: This will eventually get deleted
    json_data = json.loads(context['graph'])
    #add sidebar information to the context for display
    if 'description' in json_data['metadata']:
        context['description'] = json_data['metadata']['description'] + "</table></html>"
    else:
        context['description'] = ""

    # id of the owner of this graph
    context['owner'] = uid

    if 'name' in json_data['metadata']:
        context['graph_name'] = json_data['metadata']['name']
    else:
        context['graph_name'] = ''

    # # graph id
    context['graph_id'] = gid

    if len(json_data['graph']['edges']) > 0 and 'k' in json_data['graph']['edges'][0]['data']:
        context['filters'] = True

    # redirect if the user wishes to view the json data
    if request.method == "GET" and 'view_json' in request.GET:
        return HttpResponseRedirect("/json/%s/%s" % (uid, gid))

    return render(request, 'graphs/view_graph.html', context)

def view_json(request, uid, gid):
    '''
        View json structure of a graph.

        :param request: HTTP GET Request
        :param uid: email of the user that owns this graph
        :param gid: name of graph that the user owns
    '''
    #create a new db session
    db_session = data_connection.new_session()

    context = {}

    try:
        # Get the json of the graph that we want to view
        graph_to_view = db_session.query(graph.c.json).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    except NoResultFound:
        print uid, gid
        context['Error'] = "Graph not found, please make sure you have the correct URL."
        return render(request, 'graphs/error.html', context)

    # Get correct json for CytoscapeJS
    context['json'] = db.retrieve_cytoscape_json(graph_to_view[0])

    # id of the owner of this graph
    context['owner'] = uid

    # graph id
    context['graph_id'] = gid

    # If it is http request, render it in the specific page, otherwise just return the JSON
    if request:
        return render(request, 'graphs/view_json.html', context)
    else:
        return HttpResponse(context['json'])

def graphs(request):
    '''
        Render the My Graphs page

        :param request: HTTP GET Request
    '''

    return _graphs_page(request, 'my graphs')
    
def shared_graphs(request):
    '''
        Render the graphs/shared/ page showing all graphs that are shared with a user

        :param request: HTTP GET Request
    '''
    
    return _graphs_page(request, 'shared') 

def public_graphs(request):
    '''
        Render the graphs/public/ page showing all graphs that are public

        :param request: HTTP GET Request
    '''

    return _graphs_page(request, 'public')

def all_graphs(
    request):
    '''
        Render the graphs/all/ page showing all graphs. Admin feature [NOT CURRENTLY SUPPORTED]

        :param request: HTTP GET Request
    '''

    return _graphs_page(request, 'all')

def _graphs_page(request, view_type):
    '''
        wrapper view for the following pages:
            graphs/
            graphs/shared/
            graphs/public/
            graphs/all/

        :param request: HTTP GET Request
        :param view_type: Type of view for graph (Ex: my graphs, shared, public)
    '''
    
    #get new session from the database
    db_session = data_connection.new_session()
    
    #context of the view to be passed in for rendering
    context = {}
    graph_list = None

    #handle login
    context = login(request)

    #Send view_type to front end to tell the user (through button color) where they are
    context['view_type'] = view_type

    if context['Error']:
        return render(request, 'graphs/error.html', context)

    #check for authentication
    uid = request.session['uid']

    # pass the tag information to the front-end
    context['all_tags'] = []#db.get_all_tags(uid, view_type)

    # Set the base URL's so that the links point to the correct view types
    context['base_url'] = [] #db.get_base_urls(view_type)

    search_type = None

    if 'partial_search' in request.GET:
        search_type = 'partial_search'
    elif 'full_search' in request.GET:
        search_type = 'full_search'

    # Set all information abouut graphs to the front-end
    context = db.get_graphs_for_view_type(context, view_type, uid, request)

    # reset the search form
    context['search_form'] = SearchForm(placeholder='Search...')

    if len(context['graph_list']) == 0:
        context = constructGraphMessage(context, view_type, request.GET.get(search_type), request.GET.get('tags'))

    #Divide the results of the query into pages. Currently has poor performance
    #because the page processes a query (which may take long)
    #everytime the page loads. I think that this can be improved if
    #I store the query result in the session such that it doesn't
    #process the query unnecessarily.
    if context['graph_list'] != None:
        pager_context = pager(request, context['graph_list'])
        if type(pager_context) is dict:
            context.update(pager_context)
            for i in xrange(len(context['current_page'].object_list)):
                graph = list(context['current_page'][i])
                if request.GET.get(search_type):
                    graph[1] = db.get_all_tags_for_graph(graph[0], graph[5])
                else:
                    graph[1] = db.get_all_tags_for_graph(graph[0], graph[3])
                graph = tuple(graph)
                context['current_page'].object_list[i] = graph

    # indicator to include css/js footer for side menu support etc.
    context['footer'] = True

    return render(request, 'graphs/graphs.html', context)

def constructGraphMessage(context, view_type, search, tags):
    if view_type == 'shared':
        if search == None and tags == None:
            context['message'] = "It appears that there are no groups that have shared their graphs."
        elif search != None and tags == None:
            context['message'] = "It appears that there are no groups that have shared their graphs with the given search criteria."
        elif tags != None and search == None:
            context['message'] = "It appears that there are no groups that have shared their graphs with the given tag criteria."
        else:
            context['message'] = "It appears that there are no groups that have shared their graphs with the given search and tag criteria."

    elif view_type == 'public':
        if search == None and tags == None:
            context['message'] = "It appears that there are no public graphs available.  Please create an account and join a group or <a href='/../help/restapi/#add_graph'>upload</a> your own graphs."
        elif search != None and tags == None:
            context['message'] = "It appears that there are no public graphs available that match the search criteria.  Please create an account and join a group or <a href='/../help/restapi/#add_graph'>upload</a> your own graphs with the given search criteria."
        elif tags != None and search == None:
            context['message'] = "It appears that there are no public graphs available that match the tag criteria.  Please create an account and join a group or <a href='/../help/restapi/#add_graph'>upload</a> your own graphs with the given tag criteria."
        else:
            context['message'] = "It appears that there are no public graphs available that match the search and tag criteria.  Please create an account and join a group or <a href='/../help/restapi/#add_graph'>upload</a> your own graphs with the given search and tag criteria."

    elif view_type == 'all':
        if search == None and tags == None:
            context['message'] = "It appears that there are no graphs available."
        elif search != None and tags == None:
            context['message'] = "It appears that there are no graphs available that match the search criteria."
        elif tags != None and search == None:
            context['message'] = "It appears that there are no graphs available that match the tag criteria."
        else:
            context['message'] = "It appears that there are no graphs available that match the search and tag criteria."
    else:
        if search == None and tags == None:
            context['message'] = "It appears that you currently have no graphs uploaded. Please <a href='/../help/restapi/#add_graph'>upload</a> graphs in order to see them here."
        elif search != None and tags == None:
            context['message'] = "It appears that you currently have no graphs uploaded that match the search terms. Please <a href='/../help/restapi/#add_graph'>upload</a> graphs with the given search criteria in order to see them here."
        elif tags != None and search == None:
            context['message'] = "It appears that you currently have no graphs uploaded that match the tag terms. Please <a href='/../help/restapi/#add_graph'>upload</a> graphs with the given tag criteria in order to see them here."
        else:
            context['message'] = "It appears that you currently have no graphs uploaded that match the serach and tag terms. Please <a href='/../help/restapi/#add_graph'>upload</a> graphs with the given search and tag criteria in order to see them here."

    return context

def groups(request):
    ''' 
        Render the Owner Of page, showing groups that are owned by the user. 

        :param request: HTTP GET Request

    '''
    return _groups_page(request, 'owner of')

def groups_member(request):
    '''
        Render the Member Of page, showing the groups that the user belong to .

        :param request: HTTP GET Request

    '''
    return _groups_page(request, 'member')

def all_groups(request):
    ''' 
        Render the All Groups page, showing all groups in the database.Admin feature [NOT CURRENTLY SUPPORTED].

        :param request: HTTP GET Request

    '''
    return _groups_page(request, 'all')

def _groups_page(request, view_type):
    '''
        Wrapper view for the following pages:
            groups/
            groups/member/
            groups/public/
            groups/all/

        :param request: HTTP GET Request
        :param view_type: Type of view for the group (Example: owner of, member, public, all)

    '''

    #get new session from the database
    db_session = data_connection.new_session()

    #context of the view to be passed in for rendering
    context = {}
    group_list = None

    #handle login
    context = login(request)

    #Send view_type to front end to tell the user (through button color) where they are
    context['view_type'] = view_type

    #check for authentication
    uid = request.session['uid']
    if uid is not None:
        # Get groups that the user is a member of
        if view_type == 'member':
            group_list = db.get_all_groups_with_member(context['uid'])

        # if admin, then they can view this
        elif view_type == 'all':
            if db.is_admin(uid) == 1:
                group_list = db_session.query(group.c.group_id, group.c.name, 
                        group.c.owner_id, group.c.public).all()
            else:
                context['Error'] = "You are not authorized to see this group's contents! Please contact group's owner to add you to the group!"
                return render(request, 'graphs/error.html', context)

        #groups of logged in user(my groups)
        else:
            # List all groups that uid either owns or is a member of and also public groups.
            group_list = db.get_groups_of_user(context['uid'])

        #Order all tuples if user wants to order their results
        order_term = request.GET.get('order')

        if order_term:
            if request.GET.get('order') == 'group_ascending':
                group_list = sorted(group_list, key=lambda graph: graph[0])
            elif order_term == 'group_descending':
                group_list = sorted(group_list, key=lambda graph: graph[0], reverse=True)
            elif order_term == 'owner_ascending':
                group_list = sorted(group_list, key=lambda graph: graph[2])
            elif order_term == 'owner_descending':
                group_list = sorted(group_list, key=lambda graph: graph[2], reverse=True)

        else:
            group_list = sorted(group_list, key=lambda graph: graph[0])

        #add the group list to context to display on the page.
        if len(group_list) != 0:
            context['group_list'] = group_list
        else:
            context['group_list'] = None

        pager_context = pager(request, group_list)

        if type(pager_context) is dict:
            context.update(pager_context)

        context['my_groups'] = len(db.get_groups_of_user(context['uid']))
        context['member_groups'] = len(db.get_all_groups_with_member(context['uid']))

        if view_type == 'owner of' and context['my_groups'] == 0:
            context['message'] = "It appears that you are not an owner of any group.  Please create a group in order to own a group."
        elif view_type == 'member' and context['member_groups'] == 0 :
            context['message'] = "It appears as if you are not a member of any group. Please join a group in order for them to appear here."
        else:
            context['message'] = "It appears as if there are currently no groups on GraphSpace."
        return render(request, 'graphs/groups.html', context)

    #No public groups anymore
    else:
        context['Error'] = "You need to be logged in and also be a member of this group in order to see this group's contents!"
        return render(request, 'graphs/error.html', context)

def graphs_in_group(request, group_owner, group_id):
    '''
        Groups/group_name page, where group_name is the name of the
        group to view the graphs that belong to the group.

        This is the view displayed when the user clicks a group listed
        on the /groups page.

        Group names that are not allowed: 'all', 'member' and 'public'.
        they are preoccupied.

        :param request: HTTP GET Request
        :param group_id: Name of group to get

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
    if "uid" in context:
        if group_id != 'all' or group_id != 'member':

            group_dict = db.groups_for_user(context['uid'])

            if not any(g_dict['groupId'] == group_id for g_dict in group_dict):
                context['Error'] = "You need to be a member of a group to see its contents!  Please contact group's owner to add you to the group!"
                return render(request, 'graphs/error.html', context)

            # Get all graph information that belong to this group
            graph_data = db.get_all_graphs_for_group(context['uid'], group_owner, group_id, request)

            search_type = None
            context['search_result'] = False
            
            if 'partial_search' in request.GET:
                search_type = 'partial_search'
            elif 'full_search' in request.GET:
                search_type = 'full_search'

            if search_type != None:
                context['search_result'] = True
                context['search_type'] = search_type
                context['search_word'] = ""

                cleaned_search_terms = request.GET.get(search_type).split(',')
                for i in xrange(len(cleaned_search_terms)):
                    cleaned_search_terms[i] = cleaned_search_terms[i].strip()
                    # Deleted no length search terms
                    if len(cleaned_search_terms[i]) == 0:
                        del cleaned_search_terms[i]

                for i in xrange(len(cleaned_search_terms)):
                    context['search_word'] += cleaned_search_terms[i] + ','

                if len(context['search_word']) > 0: 
                    context['search_word'] = context['search_word'][:len(context['search_word']) - 1]

            # include the graph data to the context
            if len(graph_data) != 0:
                context['graph_list'] = graph_data
            else:
                context['graph_list'] = None
                if context['search_result'] == True:
                    context['message'] = "It appears as if there are no graphs in this group that match your search query!"
                else:
                    context['message'] = "It appears as if there are no graphs in this group yet."

            group_information = db.get_group_by_id(group_owner, group_id)

            # pass the group_id to the context for display
            context['group_id'] = group_information[0][4]

            context['group_name'] = group_information[0][3]

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
                for i in xrange(len(context['current_page'].object_list)):
                    graph = list(context['current_page'][i])
                    if request.GET.get('search'):
                        graph[1] = db.get_all_tags_for_graph(graph[0], graph[5])
                    else:
                        graph[1] = db.get_all_tags_for_graph(graph[0], graph[3])
                    graph = tuple(graph)
                    context['current_page'].object_list[i] = graph

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
    else:
        context['Error'] = "Please log in to view groups page"
        return render(request, 'graphs/error.html', context)

def help(request):
    '''
        Render the following pages:

        help/
        help/getting_started

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_users.html', context)

def help_programmers(request):
    '''
        Render the help/tutorials page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_programmers.html', context)

def help_graphs(request):
    '''
        Render the help/graphs page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_graphs.html', context)

def help_restapi(request):
    '''
        Render the help/restapi page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_restapi.html', context)

def help_jsonref(request):
    '''
        Render the help/jsonref page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_jsonref.html', context)

def help_about(request):
    '''
        Render the help/about page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_about.html', context)

def register(request):
    '''
        Register a new user.

        :param request: HTTP POST Request containing:

        {"user_id": <user_id>, "password": <password>}

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
                return HttpResponse(json.dumps(db.throwError(400, "Email already exists!")), content_type="application/json");
            
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
            db_base = Database('prod')
            user = db_base.meta.tables['user']

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
            conn = db_base.connect()
            # execute the insert statement
            # see Executing part at
            # http://docs.sqlalchemy.org/en/rel_0_9/core/tutorial.html#coretutorial-insert-expressions 
            conn.execute(new_user)
            # close connection
            db_base.close()

            # should display success message. not there yet.
            return HttpResponseRedirect('/index/')
    else:
        register_form = RegisterForm() # An unbound form

    context['register_form'] = register_form
    context['footer'] = True

    return render(request, 'graphs/register.html', context)

def retrieveIDs(request):
    '''
        Retrieves ID's of the nodes.
        Used when highlighting elements of the graph.

        :param request: HTTP POST Request containing

        {uid: <user_id>, gid: <graph_id>, values: [labels/id's of edges/nodes return id for]}

        :return JSON: {"IDS": [ids of nodes/edges in database]}

    '''

    #Grab id's of the nodes to highlight given the label of the nodes
    if request.POST:
        db_session = data_connection.new_session()
        element_values = request.POST['values'].split(',')
        elementDictionary = {}
        for element in element_values:
            elementDictionary[element] = []
            # Find an edge
            if ':' in element:
                elementDictionary[element] += db.find_edge(request.POST['uid'], request.POST['gid'], element.strip(), request.POST['search_type'])
            else:
                elementDictionary[element] += db.find_node(request.POST['uid'], request.POST['gid'], element.strip(), request.POST['search_type'])

        return HttpResponse(json.dumps(elementDictionary))
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def logout(request):
    '''
        Log the user out and display logout page.

        :param request: HTTP GET Request

    '''
    context = {}
    
    try:
        del request.session['uid']
    except KeyError:
        # TODO: should something be done here?
        pass

    # redirect to the main page after logout.
    return HttpResponseRedirect('/index/')

def sendResetEmail(request):
    '''
        Sends an email to the requester.

        :param request: HTTP POST Request containing:

        {"forgot_email": <user_id>}

        :returns JSON: {"Error|Success": "Email does not exist! | "Email has been sent!"}

    '''
    db.add_user_to_password_reset(request.POST['forgot_email'])
    emailId = db.sendForgotEmail(request.POST['forgot_email'])

    # If email is not found, throw an error
    if emailId == None:
        return HttpResponse(json.dumps(db.throwError(404, "Email does not exist!")), content_type="application/json");

    return HttpResponse(json.dumps(db.sendMessage(200, "Email has been sent!")), content_type="application/json");

def resetLink(request):
    '''
        Directs the user to a link that
        allows them to change their password.

        :param HTTP GET Request
        :return JSON: {"email": <user_id> | "Error": "Unrecognized ID"}

    '''
    code = request.GET.get('id')
    email = db.retrieveResetInfo(code)

    if email == None:
        return HttpResponse(json.dumps(db.throwError(400, "Unrecognized ID")), content_type="application/json");

    context = {"email": email, "url": URL_PATH}

    return render(request, 'graphs/reset.html', context)

def resetPassword(request):
    '''
        Resets the password of the user.

        :param request: HTTP POST Request containing

        {"email": <user_id>, "password": "password"}

        :return JSON: {"Error|Success": "Password Update not successful! | Password updated for <user_id>!"}

    '''
    resetInfo = db.resetPassword(request.POST['email'], request.POST['password'])

    if resetInfo == None:
        return HttpResponse(json.dumps(db.throwError(500, "Password Update not successful!")), content_type="application/json");

    return HttpResponse(json.dumps(db.sendMessage(200, "Password updated for " + request.POST['email'])), content_type="application/json");


def save_layout(request, uid, gid):
    '''
        Saves a layout for a graph.

        :param HTTP POST Request

    '''
    result = db.save_layout(request.POST['layout_id'], request.POST['layout_name'], uid, gid, request.POST['loggedIn'], request.POST['points'], request.POST['public'], request.POST['unlisted'])
    if result == None:
        return HttpResponse(json.dumps(db.sendMessage(200, "Layout saved!")), content_type="application/json")
    
    return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json");

def download(request):
    '''
        Download the graph as an image.

        :param HTTP GET Request

    '''

    if request.POST:
        if request.POST['image']:
            response =  HttpResponse(request.POST['image'], content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="foo.png"'
            return response

def changeLayoutName(request):
    '''
        Changes the name of the layout

        :param request: Incoming HTTP POST Request containing:

        {"uid": <username>,"gid": <name of graph>, "old_layout_name": <name of old layout>, "new_layout_name": <new name of layout>"}

        :return JSON:  {"Success": <message>}
    '''
    if request.method == 'POST':
        uid = request.POST['uid']
        gid = request.POST['gid']
        old_layout_name = request.POST['old_layout_name']
        new_layout_name = request.POST['new_layout_name']
        loggedIn = request.POST['loggedIn']

        db.changeLayoutName(uid, gid, old_layout_name, new_layout_name, loggedIn)
        return HttpResponse(json.dumps({"StatusCode": 200, "Message": "Layout name changed!", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/?layout=' + new_layout_name}), content_type="application/json")

def deleteLayout(request):
    '''
        Deletes layout of a graph

        :param request: Incoming HTTP POST Request containing:

        {"owner": <owner of graph>,"gid": <name of graph>, "layout": <name of layout to delete>, "user_id": <layout that user belongs to>"}

        :return JSON:  {"Success": <message>}
    '''
    if request.method == 'POST':
        uid = request.POST['owner']
        gid = request.POST['gid']
        layoutToDelete = request.POST['layout']
        loggedIn = request.POST['user_id']

        result = db.deleteLayout(uid, gid, layoutToDelete, loggedIn)

        if result == None:
            return HttpResponse(json.dumps({"StatusCode": 200, "Message": "Layout deleted!", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/'}), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")

def makeLayoutPublic(request):
    '''
        Makes a layout of graph public

        :param request: Incoming HTTP POST Request containing:

        {"owner": <owner of graph>,"gid": <name of graph>, "layout": <name of layout to delete>, "user_id": <layout that user belongs to>"}

        :return JSON:  {"Success": <message>}
    '''
    if request.method == 'POST':
        uid = request.POST['owner']
        gid = request.POST['gid']
        layoutToMakePpublic = request.POST['layout']
        loggedIn = request.POST['user_id']

        db.makeLayoutPublic(uid, gid, layoutToMakePpublic, loggedIn)
        return HttpResponse(json.dumps({"StatusCode": 200, "Message": "Layout made public!", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/?layout=' + new_layout_name}), content_type="application/json")


def getGroupsForGraph(request):
    '''
        Returns all the groups that are associated with request.

        :param request:Incoming HTTP POST Request containing:

        {"gid": <name of graph>, "owner": <owner of the graph>}

        :return JSON: {"Groups": [list of groups]}
    '''
    if request.method == 'POST':
        owner = request.POST['owner']
        gid = request.POST['gid']
        
        return HttpResponse(json.dumps({"StatusCode": 200, "Group_Information": db.get_all_groups_for_user_with_sharing_info(owner, gid)}), content_type="application/json")

def shareGraphWithGroups(request):
    '''
        Shares graph with specified groups.
        Unshares graph with specified groups.

        :param request:Incoming HTTP POST Request containing:
        {"gid": <name of graph>, "owner": <owner of the graph>, "groups_to_share_with": [group_ids], "groups_not_to_share_with": [group_ids]}
        :return TBD
    '''
    if request.method == 'POST':
        owner = request.POST['owner']
        gid = request.POST['gid']
        groups_to_share_with = request.POST.getlist('groups_to_share_with[]')
        groups_not_to_share_with = request.POST.getlist('groups_not_to_share_with[]')

        for group in groups_to_share_with:
            groupInfo = group.split("12345__43121__")
            db.share_graph_with_group(owner, gid, groupInfo[0], groupInfo[1])

        for group in groups_not_to_share_with:
            groupInfo = group.split("12345__43121__")
            db.unshare_graph_with_group(owner, gid, groupInfo[0], groupInfo[1])

        return HttpResponse("Done")

    else:
        return HttpResponse("Test")

def create_group(request, groupname):
    '''
        Allows group creation from the GUI.

        :param request: Incoming HTTP POST Request containing:

        {"owner": <owner of group>, "groupname": < name of group>, "username": User who submitted the request}

        :return JSON: {"Upload": <message>, "Group Name | Error": <message> }
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        group_created = db.create_group(request.POST['username'], groupname)
        
        # If there isn't already a group name that exists with the same name under account
        # add it to account
        if group_created != None:
            return HttpResponse(json.dumps({"StatusCode": 201, "Message": "Group created!", "Group Name": group_created[0], "Group Id": group_created[1]}, indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, "Group name already exists for this account"), indent=4, separators=(',', ': ')), content_type="application/json")

def deleteGraph(request):
    '''
        Allows deletion of graph.

        :param request: Incoming HTTP POST Request containing:

        {"uid": <owner of graph>, "gid": < name of graph>}

        :return JSON: {"Delete": <message>}
    '''
    if request.method == 'POST':
        user_id = request.POST['uid']
        graphname = request.POST['gid']
        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            db.delete_graph(request.POST['uid'], request.POST['gid'])
            return HttpResponse(json.dumps(db.sendMessage(200, "Successfully deleted " + graphname + " owned by " + user_id + '.'), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(404, "No Such Graph Exists."), indent=4, separators=(',', ': ')), content_type="application/json")

def delete_group_through_ui(request):
    '''
        Allows group creation from the GUI.

        :param request: Incoming HTTP POST Request containing:

        {"groupOwner": <owner of group>, "groupName": < name of group>, "username": User who submitted the request}

        :return JSON: {"Delete": <message>}
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        if request.POST['username'] == request.POST['groupOwner']:
            db.remove_group(request.POST['groupOwner'], request.POST['groupName'])
            return HttpResponse(json.dumps(db.sendMessage(200, request.POST['groupName'] + " deleted for " + request.POST['groupOwner'])), content_type="application/json")

def unsubscribe_from_group(request):
    '''
        Allows group creation from the GUI.

        :param request: Incoming HTTP POST Request containing:

        {"groupOwner": <owner of group>, "groupName": < name of group>, "username": User who submitted the request}

        :return JSON: {"Unsubscribe | Error": <message>}
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        result = db.remove_user_through_ui(request.POST['username'], request.POST['groupOwner'], request.POST['groupName'])
        if result != None:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "You are no longer following " + request.POST['groupName'] + " owned by " + request.POST['groupOwner'])), content_type="application/json")

def change_description_through_ui(request):
    '''
        Allows user to change description of group through UI.

        :param request: Incoming HTTP POST Request containing:

        {"groupOwner": <owner of group>, "groupId": < ID of group>, "username": User who submitted the request, "description": <description>}

        :return JSON: {"Changed | Error": <message>}
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        result = db.change_description(request.POST['username'], request.POST['groupId'], request.POST['groupOwner'], request.POST['description'])
        if result != None:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "Changed description")), content_type="application/json")

def add_member_through_ui(request):
    '''
        Allows user to add members to a group through UI.

        :param request: Incoming HTTP POST Request containing:

        {"groupOwner": <owner of group>, "groupId": < ID of group>, "member": "member to add"}

        :return JSON: {"Message": <message>}
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        result = db.add_user_to_group(request.POST['member'], request.POST['groupOwner'], request.POST['groupId'])
        return HttpResponse(json.dumps(db.sendMessage(200, result)), content_type="application/json")

def remove_member_through_ui(request):
    '''
        Allows user to remove members from a group through UI.

        :param request: Incoming HTTP POST Request containing:

        {"groupOwner": <owner of group>, "groupId": < ID of group>, "member": "member to remove"}

        :return JSON: {"Message": <message>}
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        result = db.remove_user_from_group(request.POST['member'], request.POST['groupOwner'], request.POST['groupId'])
        return HttpResponse(json.dumps(db.sendMessage(200, result)), content_type="application/json")



def getGroupsWithLayout(request):
    '''
        Gets all groups that have the particular graph shared in the group.

        :param request: Incoming HTTP POST Request containing:

        {"loggedIn": [current user], "owner": < Owner of graph >, "gid": "Id of graph"}

        :return JSON: {"Groups":[Groups]}
    '''
    if request.method == 'POST':
        result = db.is_layout_shared(request.POST['layout'], request.POST['loggedIn'], request.POST['owner'], request.POST['gid'])
        return HttpResponse(json.dumps({"StatusCode": 200, "Group_Information": result}), content_type="application/json")
    else:
        return HttpResponse("NONE")

def setDefaultLayout(request):
    if request.method == 'POST':
        result = db.setDefaultLayout(request.POST['layoutId'], request.POST['gid'], request.POST['uid'])
        if result != None:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "Set " + request.POST['layoutId'] + " as default")), content_type="application/json")
    else:
        return HttpResponse("NONE")

def removeDefaultLayout(request):
    if request.method == 'POST':
        result = db.removeDefaultLayout(request.POST['layoutId'], request.POST['gid'], request.POST['uid'])
        if result != None:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "Removed " + request.POST['layoutId'] + " as default")), content_type="application/json")
    else:
        return HttpResponse("NONE")

def renderImage(request):
    return HttpResponseRedirect(URL_PATH + 'static/images/legend.png');

def upload_graph_through_ui(request):

    if request.method == 'POST':
            print 'HERE'
            print request.POST
            login_form = LoginForm()
            register_form = RegisterForm()
            
            if request.POST['email'] == 'Public User':
                # assign random id generator
                result = db.uploadCyjsFile(None, request.FILES['graphname'].read())
                if 'Error' not in result:
                    context = {'login_form': login_form, 'register_form': register_form, 'Success': result['Success']}
                else:
                    context = {'login_form': login_form,  'register_form': register_form, 'Error': result['Error']}
                return render(request, 'graphs/upload_graph.html', context)
            else:
                result = db.uploadCyjsFile(request.POST['email'], request.FILES['graphname'].read())
                if 'Error' not in result:
                    context = {'login_form': login_form,  'uid': request.POST['email'], 'register_form': register_form, 'Success': result['Success']}
                else:
                    context = {'login_form': login_form,  'uid': request.POST['email'], 'register_form': register_form, 'Error': result['Error']}
                return render(request, 'graphs/upload_graph.html', context)
    else: 
        context = login(request)
        print context
        return render(request, 'graphs/upload_graph.html', context)

def shareLayoutWithGroups(request):
    '''
        Shares graph with specified groups.
        Unshares graph with specified groups.

        :param request:Incoming HTTP POST Request containing:
        {"gid": <name of graph>, "owner": <owner of the graph>, "groups_to_share_with": [group_ids], "groups_not_to_share_with": [group_ids]}
        :return TBD
    '''
    if request.method == 'POST':
        owner = request.POST['owner']
        gid = request.POST['gid']
        uid = request.POST['uid']
        layoutId = request.POST['layoutId']

        if len(db.get_all_groups_for_this_graph(owner, gid)) == 0:
            return HttpResponse(json.dumps(db.throwError(400, "No groups to share with.  Either share this graph with a group first or make this graph public!")), content_type="application/json")
        else:
            if db.is_public_graph(owner, gid):
                db.makeLayoutPublic(owner, gid, layoutId, uid)
            else:
                db.share_layout_with_all_groups_of_user(owner, gid, layoutId)
        ## SHELVE THIS FOR NOW (ALLOW USER TO CHOOSE WHICH GROUPS TO SHARE LAYOUT WITH)
        # groups_to_share_with = request.POST.getlist('groups_to_share_with[]')
        # groups_not_to_share_with = request.POST.getlist('groups_not_to_share_with[]')
        # layoutId = request.POST['layoutId']

        # for group in groups_to_share_with:
        #     groupInfo = group.split("12345__43121__")
        #     db.share_layout_with_group(layoutId, owner, gid, groupInfo[0], groupInfo[1])

        # for group in groups_not_to_share_with:
        #     groupInfo = group.split("12345__43121__")
        #     db.unshare_layout_with_group(layoutId, owner, gid, groupInfo[0], groupInfo[1])
        ##

            return HttpResponse(json.dumps(db.sendMessage(200, "Okay")), content_type="application/json")

##### END VIEWS #####

##### REST API #####

def upload_graph(request, user_id, graphname):
    '''
        Uploads a graph for a user

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :param user_id: Id of the user
        :param graphname: Name of the graph
        
        :return response: JSON Response: {"Success|Error": <message>}

    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        graph_errors = db.insert_graph(user_id, graphname, request.FILES['graphname'].read())
        if graph_errors != None:
            return HttpResponse(json.dumps(db.throwError(400, graph_errors), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(201, "Graph inserted into GraphSpace!"), indent=4, separators=(',', ': ')), content_type="application/json")

def update_graph(request, user_id, graphname):
    '''
        Updates an already existing graph.

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :param user_id: Id of the user
        :param graphname: Name of the graph
        
        :return response: JSON Response: {"Success|Error": <message>}
    '''

    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        graph_errors = db.update_graph(user_id, graphname, request.FILES['graphname'].read())
        if graph_errors != None:
            return HttpResponse(json.dumps(db.throwError(404, graph_errors), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(201, "Updated " + graphname + " for " + user_id + '.'), indent=4, separators=(',', ': ')), content_type="application/json")


def retrieve_graph(request, user_id, graphname):
    '''
        Retrieves the json of a specified graph

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :param user_id: Id of the user
        :param graphname: Name of the graph
        
        :return response: JSON Response: {"Graph|Error": <message>}
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            return HttpResponse(jsonData)
        else:
            return HttpResponse(json.dumps(db.throwError(404, "No Such Graph Exists!"), indent=4, separators=(',', ': ')), content_type="application/json")

def remove_graph(request, user_id, graphname):
    '''
        Removes a graph from the server

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :param user_id: Id of the user
        :param graphname: Name of the graph
        
        :return response: JSON Response: {"Success|Error": <message>}

    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")
  
        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            db.delete_graph(user_id, graphname)
            return HttpResponse(json.dumps(db.sendMessage(200, "Successfully deleted " + graphname + " owned by " + user_id + '.'), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(404, "No Such Graph Exists."), indent=4, separators=(',', ': ')), content_type="application/json")

def view_all_graphs_for_user(request, user_id):
    '''
        View all graphs for a user

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :return response: JSON Response: {"Graphs|Error": <message>}
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        data = db.get_all_graphs_for_user(user_id)
        return HttpResponse(json.dumps({"StatusCode": 200, "Graphs": data}, indent=4, separators=(',', ': ')), content_type="application/json")

def make_graph_public(request, user_id, graphname):
    '''
        Makes specified graph and all of its layouts public

        :param request: Incoming HTTP POST Request containing:
        {"username": <username>,"password": <password>}
        :param graphname: name of graph to make public
        :return response: JSON Response: {"Success|Error": <message>}
    '''
    if request.method == 'POST':
        
        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")
        
        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        data = db.change_graph_visibility(1, request.POST['username'], graphname)

        if data == None:
            return HttpResponse(json.dumps(db.sendMessage(200, "Successfully made " + graphname + " owned by " + user_id + " public."), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(404, data), indent=4, separators=(',', ': ')), content_type="application/json")

def make_graph_private(request, user_id, graphname):
    '''
        Makes specified graph and all of its layouts public

        :param request: Incoming HTTP POST Request containing:
        {"username": <username>,"password": <password>}
        :param graphname: name of graph to make public
        :return response: JSON Response: {"Success|Error": <message>}
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")
        
        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        data = db.change_graph_visibility(0, request.POST['username'], graphname)
        if data == None:
            return HttpResponse(json.dumps(db.sendMessage(200, "Successfully made " + graphname + " owned by " + user_id + " private."), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(404, data), indent=4, separators=(',', ': ')), content_type="application/json")

def get_groups(request):
    '''
        Get all groups that are on this server

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :return response: JSON Response: {"Groups|Error": <message>}
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        data = db.get_all_groups_in_server()
        return HttpResponse(json.dumps({"StatusCode": 200, "Groups": data}, indent=4, separators=(',', ': ')), content_type="application/json")

def get_group(request, group_owner, groupname):
    '''
        Get information about this group 

        :param request: Incoming HTTP POST Request containing: {"username": <username>,"password": <password>}
        :param group_owner: Owner of group to get from server
        :param groupname: ID of group to get from server
        :return response: JSON Response: {"Groups|Error": <message>}

    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        data = db.get_group(group_owner, groupname)
        if data == None:
            return HttpResponse(json.dumps(db.throwError(404, "Group does not exist for this user!"), indent=4, separators=(',', ': ')), content_type="application/json")
        
        return HttpResponse(json.dumps({"StatusCode": 200, "Groups": data}, indent=4, separators=(',', ': ')), content_type="application/json");


def delete_group(request, group_owner, groupname):
    '''
        Deletes a group from the server.
        
        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}
        :param groupname: Name of group to delete from server

        :return response: JSON Response: {"Success|Failure": <message>}

    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if group_owner == request.POST['username']:
            data = db.remove_group(request.POST['username'], groupname)
            return HttpResponse(json.dumps(db.sendMessage(200, data), indent=4, separators=(',', ': ')), content_type="application/json");
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The group owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")


def add_group(request, group_owner, groupname):
    '''
        Adds a group to the server.  If groupname already exists under a user account, then it will fail, otherwise a group name is created under the user's account.

        :param request: Incoming HTTP POST Request containing:
        
        {"username": <username>,"password": <password>}

        :param group: Name of group to add to server
        :return response: JSON Response: {Upload: "Success|Failure", "Group Name|Error": group | error}
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")
        
        if group_owner == request.POST['username']:
            data = create_group(request, groupname)
            return HttpResponse(data)
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The group owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")

def get_group_for_user(request, user_id):
    '''
        Gets all groups that a user is a part of.  

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :param user_id: Email of the user to get the groups for
        :return JSON Response: {"User": <user_id>, "Groups": <name of groups for the user>}

    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        group = db.groups_for_user(user_id)
        return HttpResponse(json.dumps({"StatusCode": 200, "Groups": group}, indent=4, separators=(',', ': ')), content_type="application/json")

def add_user_to_group(request, group_owner, groupname, user_id):
    '''
        Adds specified user to a group.

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}    

        :param groupname: Name of group to add user to
        :param user_id: Email of user to add to the group
        :return JSON Response: {"Response": <response>}
    '''

    if request.method == 'POST':

        # Check to see if the user/password is acceptable
        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if group_owner == request.POST['username']:
            # Adds user to group
            data = db.add_user_to_group(user_id, request.POST['username'], groupname)

            # If nothing is returned, that means that something went wrong
            if data == None:
                return  HttpResponse(json.dumps(db.throwError(400, "Group doesn't exist or user has already been added!"), indent=4, separators=(',', ': ')), content_type="application/json")

            return HttpResponse(json.dumps(db.sendMessage(200, data), indent=4, separators=(',', ': ')), content_type="application/json")

        else:
            return HttpResponse(json.dumps(db.throwError(400, "The group owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")


def remove_user_from_group(request, group_owner, groupname, user_id):
    '''
        Removes user from group

        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}    
        :param groupname: Name of group to remove user from
        :param user_id: Email of user to remove

    '''

    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")
        if group_owner == request.POST['username']:
            group = db.remove_user_from_group(user_id, request.POST['username'], groupname)
            return HttpResponse(json.dumps(db.sendMessage(200, group), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The group owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")

def share_graph(request, graphname, group_owner, groupname):
    '''
        Share a graph with group.

        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param graphname: Name of graph to unshare_graph
        :param groupname: Name of group to unshare graph with

        :return JSON: {"Response": <message>}
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        result = db.share_graph_with_group(request.POST['username'], graphname, groupname, group_owner)
        if result == None:
            return HttpResponse(json.dumps(db.sendMessage(200, "Graph successfully shared with group!"), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(400, result), indent=4, separators=(',', ': ')), content_type="application/json")

def unshare_graph(request, graphname, group_owner, groupname):
    '''
        Unshare a graph from a group.

        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param graphname: Name of graph to unshare_graph
        :param groupname: Name of group to unshare graph with

        :return JSON: {"Response": <message>}
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        result = db.unshare_graph_with_group(request.POST['username'], graphname, groupname, group_owner)
        if result == None:
            return HttpResponse(json.dumps(db.sendMessage(200, "Graph successfully unshared with group!"), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(400, result), indent=4, separators=(',', ': ')), content_type="application/json")

def get_tags_for_user(request, username):
    '''
        Get all tags that a user has under their name
        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param username: Name of user to get tags from

        :return JSON: {"Response": <message>}
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        result = db.get_all_tags_for_user(username)
        return HttpResponse(json.dumps({"StatusCode": 200, "Tags": result}, indent=4, separators=(',', ': ')), content_type="application/json")

def get_all_tags_for_graph(request, username, graphname):
    '''
        Get all tags that a user has under their graph
        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param graphname: Name of graph to get tags from
        :param username: Name of user to get graph of

        :return JSON: {"Response": <message>}
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")


        result = db.get_all_tags_for_graph(graphname, username)
        return HttpResponse(json.dumps({"StatusCode": 200, "Tags": result}, indent=4, separators=(',', ': ')), content_type="application/json")

def get_all_graphs_for_tags(request, tag):
    '''
        Get all graphs associated with these tags
        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param tag: Name of tag to get graphs of 

        :return JSON: {"Response": <message>}
    '''
    
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        result = db.get_all_graphs_for_tags(tag)
        return HttpResponse(json.dumps({"StatusCode": 200, "Graphs": result}, indent=4, separators=(',', ': ')), content_type="application/json")

def make_all_graphs_for_tag_public(request, username, tagname):
    '''
        Makes all graphs with this tag public
        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param username: Owner of graphs to change 
        :param tag: Name of tag to get graphs of 

        :return JSON: {"Response": <message>}
    '''

    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if username == request.POST['username']:
            error = db.change_graph_visibility_for_tag(1, tagname, username)
            if error == None:
                return HttpResponse(json.dumps(db.sendMessage(200, "Graphs with tag have been made public"), indent=4, separators=(',', ': ')), content_type="application/json")
            else:
                return HttpResponse(json.dumps(db.throwError(400, error), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The tag owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")

def make_all_graphs_for_tag_private(request, username, tagname):
    '''
        Makes all graphs with this tag private
        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param username: Owner of graphs to change 
        :param tag: Name of tag to get graphs of 

        :return JSON: {"Response": <message>}
    '''

    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if username == request.POST['username']:
            error = db.change_graph_visibility_for_tag(0, tagname, username)
            if error == None:
                return HttpResponse(json.dumps(db.sendMessage(200, "Graphs with tag have been made private"), indent=4, separators=(',', ': ')), content_type="application/json")
            else:
                return HttpResponse(json.dumps(db.throwError(400, error), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The tag owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")

def delete_all_graphs_for_tag(request, username, tagname):
    '''
        Makes all graphs with this tag private
        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}
        :param username: Owner of graphs to change 
        :param tag: Name of tag to get graphs of 

        :return JSON: {"Response": <message>}
    '''

    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if username == request.POST['username']:
            db.delete_all_graphs_for_tag(tagname, username)
            return HttpResponse(json.dumps(db.sendMessage(200, "Graphs with tag have been deleted"), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The tag owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")
















