from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic

from graphs.util.db_conn import Database
from graphs.util.paginator import pager
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

##### VIEWS #####
def index(request):
    '''Render the main page'''

    # db.insert_all_edges_from_json()

    # handle login.
    # see graphs.auth.login for details
    context = login(request)

    if context['Error'] != None:
        return HttpResponse(json.dumps({"Error": context['Error']}), content_type="application/json");

    # If there is someone logged in, return the 'my graphs' page, otherwise redirect to inital screen
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

    # if the graph is public, or if a user is a member 
    # of the group where this graph is shared
    # or if he owns this graph, then allow him to view it
    # otherwise do not allow it
    if db.is_public_graph(uid, gid):
        graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    elif request.session['uid'] == None:
        return HttpResponse("Not Authorized to view this.")
    else:
        # If the user is member of group where this graph is shared
        user_is_member = db.can_see_shared_graph(context['uid'], uid, gid)

        # if admin, then they can see everything
        if db.is_admin(request.session['uid']) == 1 or request.session['uid'] == uid or user_is_member == True:
            graph_to_view = db_session.query(graph.c.json, graph.c.public, graph.c.graph_id).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
        else:
            return HttpResponse("Not Authorized to view this!")

    # Get correct layout for the graph to view
    context = db.set_layout_context(request, context, uid, gid)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])
    context['draw_graph'] = True

    # Get all the groups that are shared for this graph
    shared_groups = db.get_all_groups_for_this_graph(graph_to_view[2])
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
    '''
    #create a new db session
    db_session = data_connection.new_session()

    context = {}

    try:
        # Get the json of the graph that we want to view
        graph_to_view = db_session.query(graph.c.json).filter(graph.c.user_id==uid, graph.c.graph_id==gid).one()
    except NoResultFound:
        print uid, gid
        return HttpResponse('<h1>Graph not found</h1>')

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
    ''' Render the Owner Of page, showing groups that are owned by the user. '''
    return _groups_page(request, 'owner of')

def groups_member(request):
    ''' Render the Member Of page, showing the groups that the user belong to .'''
    return _groups_page(request, 'member')

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
        # Get groups that the user is a member of
        if view_type == 'member':
            group_list = db.info_groups_for_user(uid)

        # if admin, then they can view this
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

        #add the group list to context to display on the page.
        if len(group_list) != 0:
            context['group_list'] = group_list
        else:
            context['group_list'] = None

        pager_context = pager(request, group_list)

        if type(pager_context) is dict:
            context.update(pager_context)

        return render(request, 'graphs/groups.html', context)

    #No public groups anymore
    else:
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

def retrieveIDs(request):
    '''
        This retrieves ID's of the nodes.
        Used when highlighting elements of the graph.
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
    return HttpResponse(db.save_layout(request.POST['layout_id'], request.POST['layout_name'], uid, gid, uid, request.POST['points'], request.POST['public'], request.POST['unlisted']))

def download(request):
    if request.POST:
        if request.POST['image']:
            response =  HttpResponse(request.POST['image'], content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="foo.png"'
            return response

##### END VIEWS #####

##### REST API #####

def upload_graph(request, user_id, graphname):
    '''
        Uploads a graph for a user
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        graph_exists = db.insert_graph(user_id, graphname, request.FILES['graphname'].read())
        if graph_exists != None:
            return HttpResponse("Graph with " + graphname + " exists under " + user_id)
        else:
            return HttpResponse("Graph inserted into GraphSpace!")

def retrieve_graph(request, user_id, graphname):
    '''
        Retrieves the json of a specified graph
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            return HttpResponse(jsonData)
        else:
            return HttpResponse("Graph not found!")

def remove_graph(request, user_id, graphname):
    '''
        Removes a graph from the server
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")
  
        jsonData = db.get_graph_json(user_id, graphname)
        if jsonData != None:
            db.delete_graph(user_id, graphname)
            return HttpResponse("Successfully deleted " + graphname + " owned by " + user_id)
        else:
            return HttpResponse("No such graph exists!")

def view_all_graphs(request, user_id):
    '''
        View all graphs for a user
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse("Usernames do not match!")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.get_all_graphs_for_user(user_id)
        return HttpResponse(json.dumps({"Graphs": data}), content_type="application/json");


def get_groups(request):
    '''
        Get all groups that are on this server
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.get_all_groups_in_server()
        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");

#too much work, come back later
def get_group(request, groupname):
    '''
        Get all members of this group 
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.get_group_by_id(groupname)
        return HttpResponse(json.dumps({"Groups": data}), content_type="application/json");


def delete_group(request, groupname):
    '''
        Deletes a group from the server
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.remove_group(request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Response": data}), content_type="application/json");


def add_group(request, groupname):
    '''
        Adds a group to the server 
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group_created = db.create_group(request.POST['username'], groupname)
        
        if group_created != None:
            return HttpResponse(json.dumps({"Upload": "Success", "Group Name": group_created}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"Upload": "Fail", "Error": "Group name already exists for this account"}), content_type="application/json")

def get_group_for_user(request, user_id):
    '''
        Gets all groups that a user is a part of
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group = db.groups_for_user(user_id)
        return HttpResponse(json.dumps({"User": user_id, "Groups": group}), content_type="application/json")

def add_user(request, groupname, user_id):
    '''
        Adds user to a group
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        data = db.add_user_to_group(user_id, request.POST['username'], groupname)

        if data == None:
            return  HttpResponse(json.dumps({"Response": "Group doesn't exist or user has already been added!"}), content_type="application/json")

        return HttpResponse(json.dumps({"Response": data}), content_type="application/json")


def remove_user(request, groupname, user_id):
    '''
        Removes user from group
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        group = db.remove_user_from_group(user_id, request.POST['username'], groupname)
        return HttpResponse(json.dumps({"Response": group}), content_type="application/json")

def share_graph(request, graphname, groupname):
    '''
        Share a graph with group
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        result = db.share_graph_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")

def unshare_graph(request, graphname, groupname):
    '''
        Unshare a graph from a group
    '''
    if request.method == 'POST':

        if db.get_valid_user(request.POST['username'], request.POST['password']) == None:
            return HttpResponse("Username/Password is not recognized!")

        result = db.unshare_graph_with_group(request.POST['username'], graphname, groupname)
        return HttpResponse(json.dumps({"Response": result}), content_type="application/json")