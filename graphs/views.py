from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic

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
from graphs.util.json_converter import convert_json

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


    # handle login.
    # see graphs.auth.login for details
    context = login(request)

    if context['Error'] != None:
        # return HttpResponse(json.dumps({"Error": context['Error']}), content_type="application/json");
        return render(request, 'graphs/index.html', context)
    # If there is someone logged in, return the 'my graphs' page, otherwise redirect to inital screen
    if request.session['uid'] != None:
        return _graphs_page(request, 'my graphs')
    return render(request, 'graphs/index.html', context)

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
    if db.is_public_graph(uid, gid):
        graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    elif request.session['uid'] == None:
        context['Error'] = "Not Authorized to view this graph, create an account and contact graph's owner for permission."
        return render(request, 'graphs/error.html', context)
    else:
        # If the user is member of group where this graph is shared
        user_is_member = db.can_see_shared_graph(context['uid'], uid, gid)

        # if admin, then they can see everything
        if db.is_admin(request.session['uid']) == 1 or request.session['uid'] == uid or user_is_member == True:
            graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
        else:
            context['Error'] = "Not Authorized to view this graph, please contact graph's owner for permission."
            return render(request, 'graphs/error.html', context)
    # Get correct layout for the graph to view
    context = db.set_layout_context(request, context, uid, gid)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])
    context['draw_graph'] = True

    # Get all the groups that are shared for this graph
    shared_groups = db.get_all_groups_for_this_graph(uid, graph_to_view[2])
    context['shared_groups'] = shared_groups

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

    # graph id
    context['graph_id'] = gid

    if 'k' in json_data['graph']['edges'][0]['data']:
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
        context['Error'] = "Graph not found, please make sure you have the correct graph name"
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

    if context['Error']:
        return render(request, 'graphs/error.html', context)

    #check for authentication
    uid = request.session['uid']

    # pass the tag information to the front-end
    context['all_tags'] = db.get_all_tags(uid, view_type)

    # Set the base URL's so that the links point to the correct view types
    context['base_url'] = db.get_base_urls(view_type)

    # Set all information abouut graphs to the front-end
    context = db.get_graphs_for_view_type(context, view_type, uid, request.GET.get('search'), request.GET.get('tags'))

    # reset the search form
    context['search_form'] = SearchForm(placeholder='Search...')

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
        :param view_type: Type of view for the group (Example: My Groups, member, public, all)

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
        # Get groups that the user is a member of
        if view_type == 'member':
            group_list = db.get_all_groups_with_member(context['uid'])

        # if admin, then they can view this
        elif view_type == 'all':
            if db.is_admin(uid) == 1:
                group_list = db_session.query(group.c.group_id, group.c.name, 
                        group.c.owner_id, group.c.public).all()
            else:
                context['Error'] = "Not Authorized to see this group's contents! Please contact group's owner to add you to the group!"
                return render(request, 'graphs/error.html', context)

        #groups of logged in user(my groups)
        else:
            # List all groups that uid either owns or is a member of and also public groups.
            group_list = db.get_groups_of_user(context['uid'])

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

        return render(request, 'graphs/groups.html', context)

    #No public groups anymore
    else:
        context['Error'] = "Need to log in to access this group's page and also be a part of this group!"
        return render(request, 'graphs/error.html', context)

def graphs_in_group(request, group_id):
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

            group_list = db.groups_for_user(context['uid'])

            if group_id not in group_list:
                context['Error'] = "You need to be a member of a group to see its contents!  Please contact group's owner to add you to the group!"
                return render(request, 'graphs/error.html', context)

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

    return render(request, 'graphs/help_getting_started.html', context)

def help_tutorials(request):
    '''
        Render the help/tutorials page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_tutorials.html', context)

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
            db = Database('prod')
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
        id_values = []
        db_session = data_connection.new_session()
        element_values = request.POST['values'].split(',')
        for element in element_values:
            element_id = None
            # Find an edge
            if ':' in element:
                element_id = db.find_edge(request.POST['uid'], request.POST['gid'], element.strip())
            else:
                element_id = db.find_node(request.POST['uid'], request.POST['gid'], element.strip())

            if element_id != None and len(element_id) > 0:
                id_values.append(element_id)
                
        return HttpResponse(json.dumps({"IDS": id_values}))
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
    emailId = db.sendForgotEmail(request.POST['forgot_email'])

    # If email is not found, throw an error
    if emailId == None:
        return HttpResponse(json.dumps({"Error": "Email does not exist!"}), content_type="application/json");

    return HttpResponse(json.dumps({"Success": "Email has been sent!"}), content_type="application/json");

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
        return HttpResponse(json.dumps({"Error": "Unrecognized ID"}), content_type="application/json");

    context = {"email": email}

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
        return HttpResponse(json.dumps({"Error": "Password Update not successful!"}), content_type="application/json");

    return HttpResponse(json.dumps({"Success": "Password updated for " + request.POST['email']}), content_type="application/json");


def save_layout(request, uid, gid):
    '''
        Saves a layout for a graph.

        :param HTTP POST Request

    '''
    return HttpResponse(db.save_layout(request.POST['layout_id'], request.POST['layout_name'], uid, gid, request.POST['loggedIn'], request.POST['points'], request.POST['public'], request.POST['unlisted']))

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
        return HttpResponse(json.dumps({"Success": "Layout name changed!", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/?layout=' + new_layout_name}), content_type="application/json")

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

        db.deleteLayout(uid, gid, layoutToDelete, loggedIn)
        return HttpResponse(json.dumps({"Success": "Layout deleted!", "url": URL_PATH + '/graphs/' + uid + '/' + gid + '/'}), content_type="application/json")

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
        return HttpResponse(json.dumps({"Success": "Layout made public!", "url": URL_PATH + uid + '/' + gid + '/'}), content_type="application/json")


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
        
        return HttpResponse(json.dumps({"Group_Information": db.get_all_groups_for_user_with_sharing_info(owner, gid)}), content_type="application/json")

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

        db.updateSharingInformationForGraph(owner, gid, groups_to_share_with, groups_not_to_share_with)
        return HttpResponse("Done")

def create_group(request, groupname):
    '''
        Allows group creation from the GUI.

        :param request: Incoming HTTP POST Request containing:

        {"owner": <owner of group>, "groupname": < name of group>}

        :return JSON: {"Upload": <message>, "Group Name | Error": <message> }
    '''

    # If request is a POST request, add it to the server
    if request.method == 'POST':
        group_created = db.create_group(request.POST['username'], groupname)
        
        # If there isn't already a group name that exists with the same name under account
        # add it to account
        if group_created != None:
            return HttpResponse(json.dumps({"Upload": "Success", "Group Name": group_created}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"Upload": "Fail", "Error": "Group name already exists for this account"}), content_type="application/json")

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
            return HttpResponse(json.dumps({"Error": "Usernames do not match!"}), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        graph_errors = db.insert_graph(user_id, graphname, request.FILES['graphname'].read())
        if graph_errors != None:
            return HttpResponse(json.dumps({"Error": graph_errors}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"Success": "Graph inserted into GraphSpace!"}), content_type="application/json")

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
            return HttpResponse(json.dumps({"Error": "Usernames do not match!"}), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            return HttpResponse(jsonData)
        else:
            return HttpResponse(json.dumps({"Error": "No Such Graph Exists"}), content_type="application/json")

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
            return HttpResponse(json.dumps({"Error": "Usernames do not match!"}), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")
  
        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            db.delete_graph(user_id, graphname)
            return HttpResponse(json.dumps({"Success": "Successfully deleted " + graphname + " owned by " + user_id}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"Error": "No Such Graph Exists"}), content_type="application/json")

def view_all_graphs_for_user(request, user_id):
    '''
        View all graphs for a user

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :return response: JSON Response: {"Graphs|Error": <message>}
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps({"Error": "Usernames do not match!"}), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        data = db.get_all_graphs_for_user(user_id)
        return HttpResponse(json.dumps({"Graphs": data}), content_type="application/json");


def get_groups(request):
    '''
        Get all groups that are on this server

        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}

        :return response: JSON Response: {"Groups|Error": <message>}
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        data = db.get_all_groups_in_server()
        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");

def get_group(request, groupname):
    '''
        Get all members of this group 

        :param request: Incoming HTTP POST Request containing: {"username": <username>,"password": <password>}
        :param groupname: Name of group to get from server
        :return response: JSON Response: {"Groups|Error": <message>}

    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        data = db.get_group(groupname)
        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");


def delete_group(request, groupname):
    '''
        Deletes a group from the server.
        
        :param request: Incoming HTTP POST Request containing:

        {"username": <username>,"password": <password>}
        :param groupname: Name of group to delete from server

        :return response: JSON Response: {"Success|Failure": <message>}

    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        data = db.remove_group(request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Success": data}), content_type="application/json");


def add_group(request, groupname):
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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        return create_group(request, groupname)

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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        group = db.groups_for_user(user_id)
        return HttpResponse(json.dumps({"User": user_id, "Groups": group}), content_type="application/json")

def add_user_to_group(request, groupname, user_id):
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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        # Adds user to group
        data = db.add_user_to_group(user_id, request.POST['username'], groupname)

        # If nothing is returned, that means that something went wrong
        if data == None:
            return  HttpResponse(json.dumps({"Error": "Group doesn't exist or user has already been added!"}), content_type="application/json")

        return HttpResponse(json.dumps({"Response": data}), content_type="application/json")


def remove_user_from_group(request, groupname, user_id):
    '''
        Removes user from group

        :param HTTP POST Request containing
        {"username": <user_id>, "password": <password>}    
        :param groupname: Name of group to remove user from
        :param user_id: Email of user to remove

    '''

    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        group = db.remove_user_from_group(user_id, request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Response": group}), content_type="application/json")

def share_graph(request, graphname, groupname):
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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        result = db.share_graph_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")

def unshare_graph(request, graphname, groupname):
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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        result = db.unshare_graph_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")

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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        result = db.get_all_tags_for_user(username)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")

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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")


        result = db.get_all_tags_for_graph(graphname, username)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")

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
            return HttpResponse(json.dumps({"Error": "Username/Password is not recognized!"}), content_type="application/json")

        result = db.get_all_graphs_for_tags(tag)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")


















