from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic
from django.templatetags.static import static

from django.shortcuts import render_to_response

from graphs.util.paginator import pager
from graphs.util import db
from graphs.auth.login import login
from forms import LoginForm, SearchForm, RegisterForm
from django.conf import settings

import json
import bcrypt
import os
import operator

from operator import itemgetter
from itertools import groupby
from graphs.forms import LoginForm, RegisterForm

URL_PATH = settings.URL_PATH

##### VIEWS #####

def image(request):
    name = request.GET.get('name', '')

    if len(name) > 0:
        return HttpResponseRedirect(URL_PATH + 'static/images/' + name + '.png')
    else:
        return HttpResponse(json.dumps(db.throwError(404, "Image not found!")), content_type="application/json")

def saveFeedback(request):

    if request.POST:
        feedback = request.POST["feedback"]
        graph_id = request.POST["graph_id"]
        user_id = request.POST["user_id"]
        layout_owner = request.POST["layout_owner"]
        layout_name = request.POST["layout_name"]

        error = db.saveFeedback(feedback, graph_id, user_id, layout_owner, layout_name)

        if error != None:
            return HttpResponse(json.dumps(db.throwError(500, error)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "Feedback saved!")), content_type="application/json")

def getFeedback(request):

    if request.POST:
        graph_id = request.POST["graph_id"]
        user_id = request.POST["user_id"]
        layout_owner = request.POST["layout_owner"]
        layout_name = request.POST["layout_name"]

        results = db.getFeedback(graph_id, user_id, layout_owner, layout_name)

        if len(results) > 0:
            return HttpResponse(json.dumps(db.sendMessage(200, results)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(500, "No feedback entered for this task!")), content_type="application/json")

def index(request):
    '''
        Render the main page

        :param request: HTTP GET Request
    '''
    # If there is a POST request made to the main page (graphspace.org/index or graphspace.org/),
    # that means that the user is trying to log on to GraphSpace.
    # If they try to log on, we first check to see if their password needs to be reset (for whatever reason).
    # The password_reset table contains all the users whose passwords need to be updated.
    # Once the user has updated their password, their name is removed from the password_reset table

    if request.method == 'POST' and db.need_to_reset_password(request.POST['user_id']) != None:
        context = {}
        
        # Forcibly clearing an existing user session (essentially logging user out) 
        request.session['uid'] = None

        # Email the user the link to reset their password
        result = db.sendForgotEmail(request.POST['user_id'])

        # Any and all errors are thrown via "Error" key in context.  This will
        # be displayed to the user on the front end through a message.
        context['Error'] = "Need to reset your password! An email has been sent to " + request.POST['user_id'] + ' with instructions to reset your password!'
        return HttpResponse(json.dumps(db.throwError(400, context['Error'])), content_type="application/json");

    # Action to login the user to GraphSpace
    context = login(request)

    if context['Error'] == None:
        return render(request, 'graphs/index.html', context)
    elif db.need_to_reset_password(request.POST['user_id']) != None:
        context = {}
        context['Error'] = "Invalid password.  Perhaps you need to reset your password!"
        # Any and all errors are thrown via "Error" key in context.  This will
        # be displayed to the user on the front end through a message.
        return HttpResponse(json.dumps(db.throwError(400, context['Error'])), content_type="application/json");
    else:
        # If there is a problem, throw error and the reason why there was a problem
        return HttpResponse(json.dumps(db.throwError(400, context['Error'])), content_type="application/json");

def logout(request):
    '''
        Log the user out and display logout page.

        :param request: HTTP GET Request

    '''

    # Clears all context
    context = {}
    
    # Deletes the "Uid" key from the session 
    # currently being tracked by Django.
    try:
        del request.session['uid']
    except KeyError:
        # TODO: should something be done here?
        pass

    # redirect to the main page after logout.
    return HttpResponseRedirect('/index/')

def download(request):
    '''
        Download the graph as an image.
        Used for when user requests to download PNG of graph.

        :param HTTP GET Request

    '''

    # Only respond if it is a POST request.
    # It will contain the image to be downloaded by the user
    if request.POST:
        if request.POST['image']:
            response =  HttpResponse(request.POST['image'], content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="foo.png"'
            return response

    else:
        # redirect to the main page
        return HttpResponseRedirect('/index/')

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

def _graphs_page(request, view_type):
    '''
        wrapper view for the following pages:
            graphs/
            graphs/shared/
            graphs/public/

        :param request: HTTP GET Request
        :param view_type: Type of view for graph (Ex: my graphs, shared, public)
    '''
    # context of the view to be passed in for rendering
    context = {}

    # List of graphs that will be returned by the request
    graph_list = None

    # handle login
    context = login(request)

    # Send view_type to front end to tell the user (through button color) where they are
    # The view_type refers to which category of graphs are being viewed (public, shared, my graphs)
    context['view_type'] = view_type

    # If there is an error, display the error 
    if context['Error']:
        return render(request, 'graphs/error.html', context)

    # Checks to see if a user is currently logged on
    uid = request.session['uid']

    # Placeholder to keep track of 
    # whether we are partially searching or
    # exact searching
    search_type = None

    # Partial search may be thought of as "contains" matching
    # Exact search may be though of as "identical" matching
    if 'partial_search' in request.GET:
        search_type = 'partial_search'
    elif 'full_search' in request.GET:
        search_type = 'full_search'

    # Set all information abouut graphs to the front-end
    # Information of graphs consists of all data for an individual graph
    # as well as any search queries and tag queries being performed
    context = db.get_graphs_for_view_type(context, view_type, uid, request)

    # Holds the amount of times a tag appears for a graph 
    all_tags = {}

    # Goes through all the graphs that are currently on a page
    if context['graph_list'] != None:
        pager_context = pager(request, context['graph_list'])
        if type(pager_context) is dict:
            context.update(pager_context)
            for i in xrange(len(context['current_page'].object_list)):
                graph = list(context['current_page'][i])
                # Get all the tags associated with current graphs and populate the 
                # tags accordion
                graph_tags = []

                if request.GET.get(search_type):
                    user_id = graph[5]
                    graph_id = graph[0]
                    graph_tags = db.get_all_tags_for_graph(graph_id, user_id)
                    graph[1] = graph_tags
                    graph.append(db.get_visibility_of_graph(user_id, graph_id))
                else:
                    user_id = graph[2]
                    graph_id = graph[0]
                    graph_tags = db.get_all_tags_for_graph(graph_id, user_id)
                    graph.insert(1, graph_tags)
                    graph.append(db.get_visibility_of_graph(user_id, graph_id))

                context['current_page'].object_list[i] = graph

    # reset the search form
    context['search_form'] = SearchForm(placeholder='Search...')

    # Checks to see if there are any tags that the user wants to search for
    request_tags = request.GET.get('tags') or request.GET.get('tag') or None

    # If there are no graphs returned by the query, then display message on
    # how to add graphs
    if len(context['graph_list']) == 0:
        context = constructGraphMessage(context, view_type, request.GET.get(search_type), request_tags)

    recent_graphs = context['graph_list']

    recent_graphs.sort(key=lambda r: r[2], reverse=True)

    if len(recent_graphs) > 250:
        recent_graphs = recent_graphs[:250]

    graph_tags = []

    for graph in recent_graphs:

        if request.GET.get(search_type):
            graph_tags = db.get_all_tags_for_graph(graph[0], graph[5])
        else:
            graph_tags = db.get_all_tags_for_graph(graph[0], graph[2])

    for tag in graph_tags:
        if len(tag) > 0:
            if tag in all_tags:
                all_tags[tag] += 1
            else:
                all_tags[tag] = 1

    sorted_tags = sorted(all_tags.items(), key=operator.itemgetter(1), reverse = True)[:10]

    all_tags_refined = [i[0] for i in sorted_tags]

    # Populates tags search bar with most used tags of last 250 graphs
    context['all_tags'] = all_tags_refined #list(set(all_tags))[:10]

    # indicator to include css/js footer for side menu support etc.
    context['footer'] = True

    return render(request, 'graphs/graphs.html', context)

def notifications(request):
    # context of the view to be passed in for rendering
    context = {}
    # handle login
    context = login(request)
    # Checks to see if a user is currently logged on
    uid = request.session['uid']
    context['notifications'] = db.get_share_graph_event_by_member_id(context['uid'])
    context['group_list'] = db.get_all_groups_with_member(context['uid']) + db.get_groups_of_user(context['uid'])
    if uid is None:
        context['Error'] = "Please log in to view notifications."
        return render(request, 'graphs/error.html', context)
    return render(request, 'graphs/notifications.html', context)


def read_notification(request):
    if request.method == 'POST':
        nid = request.POST['nid']
        uid = request.session.get('uid')
        
        # Check if the user is authenticated
        if uid == None:
            return HttpResponse(json.dumps(db.throwError(401, "You are not allowed to update this share event."), indent=4, separators=(',', ': ')), content_type="application/json")

        # if the user owns the graph only then allow him to delete it
        graph_info = db.get_share_graph_event_by_id(nid, uid)
        if graph_info == None:
            return HttpResponse(json.dumps(db.throwError(404, "There is no such share event."), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            db.update_share_graph_event(nid, 0, uid)
            return HttpResponse(json.dumps(db.sendMessage(200, "Successfully updated share event " + nid + " owned by " + uid + '.'), indent=4, separators=(',', ': ')), content_type="application/json")



def upload_graph_through_ui(request):

    if request.method == 'POST':
            login_form = LoginForm()
            register_form = RegisterForm()

            upload_json = True

            title_of_graph = None

            if 'title' in request.POST:
                title_of_graph = request.POST['title']

            if str(request.FILES['graphname'])[-4:] != "json":
                upload_json = None
            
            if request.POST['email'] == 'Public User':
                # assign random id generator
                if upload_json:
                    result = db.uploadJSONFile(None, request.FILES['graphname'].read(), title_of_graph)
                else:
                    result = db.uploadCyjsFile(None, request.FILES['graphname'].read(), title_of_graph)

                if 'Error' not in result:
                    context = {'login_form': login_form, 'register_form': register_form, 'Success': result['Success']}
                else:
                    context = {'login_form': login_form,  'register_form': register_form, 'Error': result['Error']}
                return render(request, 'graphs/upload_graph.html', context)
            else:

                if upload_json:
                    result = db.uploadJSONFile(request.POST['email'], request.FILES['graphname'].read(), title_of_graph)
                else:
                    result = db.uploadCyjsFile(request.POST['email'], request.FILES['graphname'].read(), title_of_graph)

                if 'Error' not in result:
                    context = {'login_form': login_form,  'uid': request.POST['email'], 'register_form': register_form, 'Success': result['Success']}
                else:
                    context = {'login_form': login_form,  'uid': request.POST['email'], 'register_form': register_form, 'Error': result['Error']}
                
                return render(request, 'graphs/upload_graph.html', context)
    else: 
        context = login(request)
        return render(request, 'graphs/upload_graph.html', context)

def save_layout(request, uid, gid):
    '''
        Saves a layout for a graph.

        :param HTTP POST Request

    '''
    graph_owner = uid
    if request.POST:
        if uid == None:
            return HttpResponse(json.dumps(db.throwError(500, "Must be signed in to save a layout!")), content_type="application/json")

        result = db.save_layout(gid, graph_owner, request.POST['layout_name'], request.POST['loggedIn'], request.POST['points'], request.POST['public'], request.POST['unlisted'])
        if result == None:
            return HttpResponse(json.dumps(db.sendMessage(200, "Layout saved!")), content_type="application/json")
        
        return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")

    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def update_layout(request, uid, gid):
    '''
        Updates a layout for a graph.

        :param HTTP POST Request

    '''
    if gid[len(gid) - 1] == '/':
        gid = gid[:len(gid) - 1]

    error = db.update_layout(gid, uid, request.POST['layout_name'], request.POST['loggedIn'], request.POST['points'], request.POST['public'], request.POST['unlisted'], request.POST['originalLayout'])
    if error == None:
        return HttpResponse(json.dumps(db.sendMessage(200, "Layout updated!")), content_type="application/json")
    
    return HttpResponse(json.dumps(db.throwError(400, error)), content_type="application/json");

def design_graph(request, uid, gid):
    '''
        View a graph with CytoscapeJS along with tool pallete 
        to help researcher layout of a graph.

        :param request: HTTP GET Request
        :param uid: Owner of the graph to view
        :param gid: Graph id of the graph to view
    '''

    # Context contains all the elements we want to render on the web
    # page. We fill in the various elements of context before calling
    # the render() function.
    #handle login
    # context = login(request)
    context = {
        "uid": request.session['uid'],
        "Error": None
    }

    if gid[len(gid) - 1] == '/':
        gid = gid[:len(gid) - 1]

    #TODO: Create trigger to delete older tasks (3 days)

    # if the graph is public, or if a user is a member 
    # of the group where this graph is shared
    # or if he owns this graph, then allow him to view it
    # otherwise do not allow it
    if db.is_public_graph(uid, gid) or 'Public_User_' in uid:
        graph_to_view = db.get_all_info_for_graph(uid, gid)
    elif request.session['uid'] == None:
        context['Error'] = "You are not authorized to view this graph, create an account and contact graph's owner for permission to see this graph."
        return render(request, 'graphs/error.html', context)
    else:
        # If the user is member of group where this graph is shared
        user_is_member = db.can_see_shared_graph(context['uid'], uid, gid)

        # if user is owner of graph or a member of group that shares graph
        if request.session['uid'] == uid or user_is_member == True:
            graph_info = db.getGraphInfo(uid, gid)
            if graph_info != None:
                graph_to_view =  graph_info
            else: 
                context['Error'] = "Graph: " + gid + " does not exist for " + uid + ".  Upload a graph with this name into GraphSpace in order to see it."
                return render(request, 'graphs/error.html', context)
        else:
            context['Error'] = "You are not authorized to view this graph, please contact graph's owner for permission."
            return render(request, 'graphs/error.html', context)

    # Get correct layout for the graph to view
    context = db.set_layout_context(request, context, uid, gid)

    if context['Error']:
        return render(request, 'graphs/error.html', context)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])
    context['draw_graph'] = True

    # TODO: This will eventually get deleted
    json_data = json.loads(context['graph'])

    # id of the owner of this graph
    context['owner'] = uid

    # graph id
    context['graph_id'] = gid

    # Don't display the task_view
    context["task_view"] = False
    context["approve_view"] = False
    context["researcher_view"] = False
    context["designer_view"] = True

    return render(request, 'graphs/view_graph.html', context)

def view_graph(request, uid, gid):
    '''
        View a graph with CytoscapeJS.

        :param request: HTTP GET Request
        :param uid: Owner of the graph to view
        :param gid: Graph id of the graph to view
    '''
    # Context contains all the elements we want to render on the web
    # page. We fill in the various elements of context before calling
    # the render() function.
    #handle login
    context = login(request)

    if gid[len(gid) - 1] == '/':
        gid = gid[:len(gid) - 1]

    #TODO: Create trigger to delete older tasks (3 days)

    # if the graph is public, or if a user is a member 
    # of the group where this graph is shared
    # or if he owns this graph, then allow him to view it
    # otherwise do not allow it
    if db.is_public_graph(uid, gid) or 'Public_User_' in uid:
        graph_to_view = db.get_all_info_for_graph(uid, gid)
    elif request.session['uid'] == None:
        context['Error'] = "You are not authorized to view this graph, create an account and contact graph's owner for permission to see this graph."
        return render(request, 'graphs/error.html', context)
    else:
        # If the user is member of group where this graph is shared
        user_is_member = db.can_see_shared_graph(context['uid'], uid, gid)

        # if user is owner of graph or a member of group that shares graph
        if request.session['uid'] == uid or user_is_member == True:
            graph_info = db.getGraphInfo(uid, gid)
            if graph_info != None:
                graph_to_view =  graph_info
            else: 
                context['Error'] = "Graph: " + gid + " does not exist for " + uid + ".  Upload a graph with this name into GraphSpace in order to see it."
                return render(request, 'graphs/error.html', context)
        else:
            context['Error'] = "You are not authorized to view this graph, please contact graph's owner for permission."
            return render(request, 'graphs/error.html', context)

    # Get correct layout for the graph to view
    context = db.set_layout_context(request, context, uid, gid)

    if context['Error']:
        return render(request, 'graphs/error.html', context)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])
    context['draw_graph'] = True

    # Get all the groups that are shared for this graph
    shared_groups = db.get_all_groups_for_this_graph(uid, graph_to_view[2])

    format_shared_groups = []
    for shared_group in shared_groups:
        format_shared_groups.append((shared_group.group_id, shared_group.owner_id))

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

    # If the metadata has either a name or a title (backward-compatible)
    # display it on the top of the graph
    if 'name' in json_data['metadata']:
        context['graph_name'] = json_data['metadata']['name']
    elif 'title' in json_data['metadata']:
        context['graph_name'] = json_data['metadata']['title']
    else:
        context['graph_name'] = ''

    # graph id
    context['graph_id'] = gid

    # Don't display the task_view
    context["task_view"] = False
    context["approve_view"] = False
    context["researcher_view"] = True

    # HARDCODED GROUP.. IF USER IS IN THIS GROUP, THEN ONLY THEN CAN THEY LAUNCH TASKS ON MTURK
    context["crowd_group"] = db.getCrowdEnabledGroup()

    if len(json_data['graph']['edges']) > 0 and 'k' in json_data['graph']['edges'][0]['data']:
        context['filters'] = True

    # redirect if the user wishes to view the json data
    if request.method == "GET" and 'view_json' in request.GET:
        return HttpResponseRedirect("/json/%s/%s" % (uid, gid))

    return render(request, 'graphs/view_graph.html', context)

def view_task(request, uid, gid):
    '''
        View that workers will see for a launched task.

        :param request: HTTP GET Request
        :param uid: email of the user that owns this graph
        :param gid: name of graph that the user owns
    '''

    # db.getAssignmentsForGraph(uid, gid)
    if 'uid' in request.session:
        context = login(request)
        context["task_view"] = True

    else:
        login_form = LoginForm()
        register_form = RegisterForm()
        context = {'login_form': login_form, 'register_form': register_form, "Error": None, "task_view": True}

    if gid[len(gid) - 1] == '/':
        gid = gid[:len(gid) - 1]

    graph_info = db.getGraphInfo(uid, gid)


    if graph_info != None:
        graph_to_view = graph_info
    else: 
        context['Error'] = "Task does not exist anymore!."
        return render(request, 'graphs/error.html', context)

    layout_name = request.GET.get('layout', '')
    layout_owner = request.GET.get('layout_owner', '')

    # Get correct layout for the graph to view
    context = db.set_task_layout_context(request, context, uid, gid, layout_name, layout_owner)

    if context['Error']:
        return render(request, 'graphs/error.html', context)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])

    context['draw_graph'] = True

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

    # graph id
    context['graph_id'] = gid

    # owner
    context["owner"] = uid

    context["researcher_view"] = False
    context["approve_view"] = False

    return render(request, 'graphs/view_graph.html', context)

def approve_task_expert(request):
    if 'uid' in request.session:
        context = login(request)
    else:
        context = {}

    tasks = db.getAllApproveTasks()
    all_tasks = len(tasks)
    for task in tasks:
        if task.submitted == 0:

            uid = task.user_id
            gid = task.graph_id

            graph_info = db.getGraphInfo(uid, gid)

            layout = db.getLayoutById(task.layout_id)

            context = db.set_task_layout_context(request, context, uid, gid, layout.layout_name, layout.owner_id, approve=True, expert=True)

            context['graph'] = db.retrieve_cytoscape_json(graph_info[0])
            context['remaining'] = all_tasks
            context['draw_graph'] = True
            
            context["researcher_view"] = False
            context["approve_view"] = True

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

            # graph id
            context['graph_id'] = gid

            # owner
            context["owner"] = uid

            return render(request, 'graphs/view_graph_expert.html', context)

    context['Error'] = "It appears as if there are no more graphs to lay out.  Thank you for your time!"
    return render(request, 'graphs/error.html', context)

def approve_task(request, uid, gid):
    '''
       Approve or reject a task.

        :param request: HTTP GET Request
        :param uid: email of the user that owns this graph
        :param gid: name of graph that the user owns
    '''

    if 'uid' in request.session:
        context = login(request)

    else:
        login_form = LoginForm()
        register_form = RegisterForm()
        context = {'login_form': login_form, 'register_form': register_form, "Error": None, "task_view": True}

    if gid[len(gid) - 1] == '/':
        gid = gid[:len(gid) - 1]

    graph_info = db.getGraphInfo(uid, gid)

    if graph_info != None:
        graph_to_view = graph_info
    else: 
        context['Error'] = "Task does not exist anymore!."
        return render(request, 'graphs/error.html', context)

    layout_name = request.GET.get('layout', '')
    layout_owner = request.GET.get('layout_owner', '')

    context = db.set_task_layout_context(request, context, uid, gid, layout_name, layout_owner, approve=True)

    if context['Error']:
        return render(request, 'graphs/error.html', context)

    # Convert JSON for CytoscapeJS, if needed
    context['graph'] = db.retrieve_cytoscape_json(graph_to_view[0])

    context['draw_graph'] = True
    
    context["researcher_view"] = False
    context["approve_view"] = True

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

    # graph id
    context['graph_id'] = gid

    # owner
    context["owner"] = uid

    return render(request, 'graphs/view_graph.html', context)

def submitEvaluation(request):
    '''
        Submits Evaluation for a task.
    '''

    if request.POST:

        gid = request.POST["graph_id"]
        uid = request.POST["user_id"]
        layout_name = request.POST["layout_name"]
        layout_owner = request.POST["layout_owner"]
        triangle_rating = request.POST["triangle_rating"]
        rectangle_rating = request.POST["rectangle_rating"]
        shape_rating = request.POST["shape_rating"]
        color_rating = request.POST["color_rating"]
        hit_id = request.POST["hit_id"]

        task_code = db.submitEvaluation(uid, gid, layout_name, layout_owner, triangle_rating, rectangle_rating, shape_rating, color_rating, hit_id)

        if task_code != None:
            return HttpResponse(json.dumps(db.sendMessage(201, task_code)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(500, "Evaluation Submission Unsucessful!")), content_type="application/json")
    else:
        return render(request, 'graphs/error.html', {"Error": "This route only accepts POST Requests"})

def submitExpertEvaluation(request):
    '''
        Submits Expert Evaluation for a task.
    '''

    if request.POST:

        gid = request.POST["graph_id"]
        uid = request.POST["user_id"]
        layout_name = request.POST["layout_name"]
        layout_owner = request.POST["layout_owner"]
        triangle_rating = request.POST["triangle_rating"]
        rectangle_rating = request.POST["rectangle_rating"]
        shape_rating = request.POST["shape_rating"]
        color_rating = request.POST["color_rating"]
        hit_id = request.POST["hit_id"]

        task_code = db.submitEvaluation(uid, gid, layout_name, layout_owner, triangle_rating, rectangle_rating, shape_rating, color_rating, hit_id, expert=True)

        if task_code != None:
            return HttpResponse(json.dumps(db.sendMessage(201, task_code)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(500, "Evaluation Submission Unsucessful!")), content_type="application/json")
    else:
        return render(request, 'graphs/error.html', {"Error": "This route only accepts POST Requests"})

def retrieveTaskCode(request):
    '''
        Retrieves code for a task when worker has completed task.

    '''

    if request.POST:

        gid = request.POST["graph_id"]
        uid = request.POST["user_id"]
        worked_layout = request.POST["layout_name"]
        numChanges = request.POST["numChanges"]
        timeSpent = request.POST["timeSpent"]
        events = request.POST["events"]
        hit_id = request.POST["hit_id"]

        if not gid or not uid:
            return HttpResponse(json.dumps(db.throwError(201, "Must include both graph_id and user_id in POST request.")), content_type="application/json")
        
        surveyCode = db.retrieveTaskCode(uid, gid, worked_layout, numChanges, timeSpent, events, hit_id)

        if surveyCode == None:
            surveyCode = "Task does not exist anymore!"
        return HttpResponse(json.dumps(db.sendMessage(201, surveyCode)), content_type="application/json")

    else:
        return render(request, 'graphs/error.html', {"Error": "This route only accepts POST Requests"})

def view_json(request, uid, gid):
    '''
        View json structure of a graph.

        :param request: HTTP GET Request
        :param uid: email of the user that owns this graph
        :param gid: name of graph that the user owns
    '''
    #handle login
    context = login(request)

    if gid[len(gid) - 1] == '/':
        gid = gid[:len(gid) - 1]

    # if the graph is public, or if a user is a member
    # of the group where this graph is shared
    # or if he owns this graph, then allow him to view it's JSON
    # otherwise do not allow it
    if db.is_public_graph(uid, gid) or 'Public_User_' in uid:
        graph_to_view = db.get_all_info_for_graph(uid, gid)
    elif request.session['uid'] == None:
        context['Error'] = "You are not authorized to view JSON for this graph, create an account and contact graph's owner for permission to see this."
        return render(request, 'graphs/error.html', context)
    else:
        # If the user is member of group where this graph is shared
        user_is_member = db.can_see_shared_graph(context['uid'], uid, gid)

        # if user is owner of graph or a member of group that shares graph
        if request.session['uid'] == uid or user_is_member == True:
            graph_info = db.getGraphInfo(uid, gid)
            if graph_info != None:
                graph_to_view =  graph_info
            else:
                context['Error'] = "Graph: " + gid + " does not exist for " + uid + ".  Upload a graph with this name into GraphSpace in order to see it's JSON."
                return render(request, 'graphs/error.html', context)
        else:
            context['Error'] = "You are not authorized to view JSON for this graph, please contact graph's owner for permission."
            return render(request, 'graphs/error.html', context)


    graph_to_view = db.get_graph_json(uid, gid)

    if graph_to_view == None:
        context['Error'] = "Graph not found, please make sure you have the correct URL."
        return render(request, 'graphs/error.html', context)

    # Get correct json for CytoscapeJS
    context['json'] = db.retrieve_cytoscape_json(graph_to_view)

    # id of the owner of this graph
    context['owner'] = uid

    # graph id
    context['graph_id'] = gid

    # If it is http request, render it in the specific page, otherwise just return the JSON
    if request:
        return render(request, 'graphs/view_json.html', context)
    else:
        return HttpResponse(context['json'])

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
            group_list = db.get_all_groups_with_member(context['uid']) + db.get_groups_of_user(context['uid'])

        # if admin, then they can view this
        elif view_type == 'all':
            if db.is_admin(uid) == 1:
                group_list = db.get_all_groups_in_server()
            else:
                context['Error'] = "You are not authorized to see this group's contents! Please contact group's owner to add you to the group!"
                return render(request, 'graphs/error.html', context)

        #groups of logged in user(my groups)
        else:
            # List all groups that uid either owns.
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
        context['member_groups'] = len(db.get_all_groups_with_member(context['uid'])) + context['my_groups']

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

            all_tags = []

            # Goes through all the graphs that are currently on a page
            pager_context = pager(request, graph_data)
            if type(pager_context) is dict:
                context.update(pager_context)
                for i in xrange(len(context['current_page'].object_list)):
                    graph = list(context['current_page'][i])

                    graph_tags = []
                    if request.GET.get(search_type):
                        user_id = graph[5]
                        graph_id = graph[0]
                        graph_tags = db.get_all_tags_for_graph(graph_id, user_id)
                        graph[1] = graph_tags
                        graph.append(db.get_visibility_of_graph(user_id, graph_id))
                    else:
                        user_id = graph[2]
                        graph_id = graph[0]
                        graph_tags = db.get_all_tags_for_graph(graph_id, user_id)
                        graph.insert(1, graph_tags)
                        graph.append(db.get_visibility_of_graph(user_id, graph_id))
                    all_tags += graph_tags

                    context['current_page'].object_list[i] = graph

            context['all_tags'] = list(set(all_tags))
            # indicator to include css/js footer for side menu support etc.
            context['footer'] = True

            return render(request, 'graphs/graphs_in_group.html', context)
        # if the group name is one of the designated names, display
        # appropriate vies for each
        else:
            if group_id == 'member':
                return groups_member(request)
            else:
                return public_groups(request)
    else:
        context['Error'] = "Please log in to view groups page"
        return render(request, 'graphs/error.html', context)


def features(request):
    '''
        View features page.
       
        :param request: HTTP GET Request

    '''
    #handle login
    context = login(request)

    return render(request, 'graphs/features.html', context)

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

def help_tutorial(request):
    '''
        Render the help/tutorial page.

        :param request: HTTP GET Request

    '''

    #handle login
    context = login(request)

    return render(request, 'graphs/help_tutorial.html', context)

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
            admin = 0

            db.insert_user(user_id, hashed_pw, admin)

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
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def sendResetEmail(request):
    '''
        Sends an email to the requester.

        :param request: HTTP POST Request containing:

        {"forgot_email": <user_id>}

        :returns JSON: {"Error|Success": "Email does not exist! | "Email has been sent!"}

    '''
    if request.POST:
        db.add_user_to_password_reset(request.POST['forgot_email'])
        emailId = db.sendForgotEmail(request.POST['forgot_email'])

        # If email is not found, throw an error
        if emailId == None:
            return HttpResponse(json.dumps(db.throwError(404, "Email does not exist!")), content_type="application/json")

        return HttpResponse(json.dumps(db.sendMessage(200, "Email has been sent!")), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def resetLink(request):
    '''
        Directs the user to a link that
        allows them to change their password.

        :param HTTP GET Request
        :return JSON: {"email": <user_id> | "Error": "Unrecognized ID"}

    '''
    if request.method == 'GET': 
        login_form = LoginForm()
        register_form = RegisterForm()
        code = request.GET.get('id')
        email = db.retrieveResetInfo(code)
        context = {'login_form': login_form, 'register_form': register_form}

        if email == None:
            context['Error'] = "This password reset link is outdated. Please try resetting your password again."
            return render(request, 'graphs/error.html', context)

        context['email'] = email
        context['url'] = URL_PATH
        return render(request, 'graphs/reset.html', context)
    else:
        return HttpResponse(json.dumps(db.throwError(500, "This route only accepts GET requests.")), content_type="application/json")

def resetPassword(request):
    '''
        Resets the password of the user.

        :param request: HTTP POST Request containing

        {"email": <user_id>, "password": "password"}

        :return JSON: {"Error|Success": "Password Update not successful! | Password updated for <user_id>!"}

    '''
    if request.method == "POST":
        resetInfo = db.resetPassword(request.POST['email'], request.POST['password'], request.POST['code'])

        if resetInfo == None:
            return HttpResponse(json.dumps(db.throwError(500, "Password Update not successful!")), content_type="application/json");

        return HttpResponse(json.dumps(db.sendMessage(200, "Password updated for " + request.POST['email'])), content_type="application/json");
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def launchTask(request):
    '''
        Launches a task on Amazon Mechanical Turk.

        :param request: HTTP POST Request containing

        {"graph_id": <graph_id>, "user_id": <owner of graph>}

        :return JSON: {"Error|Success": Error | Task Launched on Amazon Mechanical Turk!"}
    '''
    # Only 1 task per graph as long as there is a HIT active (3 days)
    error = db.launchTask(request.POST["graph_id"], request.POST["user_id"], request.POST.getlist('layout_array'))

    if error != None:
        return HttpResponse(json.dumps(db.throwError(500, error)), content_type="application/json")

    return HttpResponse(json.dumps(db.sendMessage(201, "Task Launched on Amazon Mechanical Turk!")), content_type="application/json");

def changeLayoutName(request):
    '''
        Changes the name of the layout

        :param request: Incoming HTTP POST Request containing:

        {"uid": <username>,"gid": <name of graph>, "old_layout_name": <name of old layout>, "new_layout_name": <new name of layout>"}

        :return JSON:  {"Success": <message>}
    '''
    if request.method == 'POST':
        loggedIn = request.session.get('uid')
        uid = request.POST['uid']
        gid = request.POST['gid']
        old_layout_name = request.POST['old_layout_name']
        new_layout_name = request.POST['new_layout_name']

        if loggedIn == None:
            return HttpResponse(json.dumps({"StatusCode": 500, "Message": "Must be logged in to make those requests", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/?layout=' + new_layout_name + "&layout_owner=" + loggedIn}), content_type="application/json")

        error = db.changeLayoutName(uid, gid, old_layout_name, new_layout_name, loggedIn)
        if error == None:
            return HttpResponse(json.dumps({"StatusCode": 200, "Message": "Layout name changed!", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/?layout=' + new_layout_name + "&layout_owner=" + loggedIn}), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, error)), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def deleteLayout(request):
    '''
        Deletes layout of a graph

        :param request: Incoming HTTP POST Request containing:

        {"owner": <owner of graph>,"gid": <name of graph>, "layout": <name of layout to delete>, "user_id": <layout that user belongs to>"}

        :return JSON:  {"Success": <message>}
    '''
    if request.method == 'POST':
        uid = request.session.get('uid')
        gid = request.POST['gid']

        if uid == None:
            return HttpResponse(json.dumps(db.throwError(500, "Must be signed in to delete a layout!")), content_type="application/json")

        layoutToDelete = request.POST['layout']
        layout_owner = request.POST['layout_owner']

        result = db.deleteLayout(uid, gid, layoutToDelete, layout_owner)

        if result == None:
            return HttpResponse(json.dumps({"StatusCode": 200, "Message": "Layout deleted!", "url": URL_PATH + 'graphs/' + uid + '/' + gid}), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def makeLayoutPublic(request):
    '''
        Makes a layout of graph public

        :param request: Incoming HTTP POST Request containing:

        {"owner": <owner of graph>,"gid": <name of graph>, "layout": <name of layout to delete>, "user_id": <layout that user belongs to>"}

        :return JSON:  {"Success": <message>}
    '''
    if request.method == 'POST':
        uid = request.POST['uid']
        gid = request.POST['gid']
        layoutToMakePpublic = request.POST['layout']
        loggedIn = request.POST['user_id']

        current_user = request.session.get('uid')

        # If user is not logged on, they can't do anything
        if current_user == None:
            return HttpResponse(json.dumps(db.throwError(500, "Must be signed in to make share layouts!")), content_type="application/json")

        # If user is the owner of the graph or if they are the layout owner, can they share a layout
        if current_user != uid and db.get_layout_for_graph(layoutId, layout_owner, gid, uid, current_user) == None:
            return HttpResponse(json.dumps(db.throwError(500, "Not authorized to share layouts!")), content_type="application/json")

        if uid == None:
            return HttpResponse(json.dumps(db.throwError(500, "Must be signed in to make a layout public!")), content_type="application/json")

        db.makeLayoutPublic(uid, gid, layoutToMakePpublic, loggedIn)
        return HttpResponse(json.dumps({"StatusCode": 200, "Message": "Layout made public!", "url": URL_PATH + 'graphs/' + uid + '/' + gid + '/?layout=' + new_layout_name}), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def getGroupsForGraph(request):
    '''
        Returns all the groups that are associated with request.

        :param request:Incoming HTTP POST Request containing:

        {"gid": <name of graph>}

        :return JSON: {"Groups": [list of groups]}
    '''
    if request.method == 'POST':
        owner = request.session.get('uid')
        gid = request.POST['gid']

        if owner == None:
            return HttpResponse(json.dumps(db.throwError(500, "Must be signed in to see groups for this graph!")), content_type="application/json")

        return HttpResponse(json.dumps({"StatusCode": 200, "Group_Information": db.get_all_groups_for_user_with_sharing_info(owner, gid)}), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def deleteGraph(request):
    '''
        Allows deletion of graph.

        :param request: Incoming HTTP POST Request containing:

        {"uid": <owner of graph>, "gid": < name of graph>}

        :return JSON: {"Delete": <message>}
    '''
    if request.method == 'POST':
        gid = request.POST['gid']
        uid = request.session.get('uid')

        # Check if the user is authenticated
        if uid == None:
            return HttpResponse(json.dumps(db.throwError(401, "You are not allowed to delete this graph"), indent=4, separators=(',', ': ')), content_type="application/json")

        # if the user owns the graph only then allow him to delete it
        graph_info = db.getGraphInfo(uid, gid)
        if graph_info == None:
            return HttpResponse(json.dumps(db.throwError(404, "You do not own any such Graph."), indent=4, separators=(',', ': ')), content_type="application/json")
        else:

            jsonData = db.get_graph_json(uid, gid)
            if jsonData != None:
                db.delete_graph(uid, gid)
                return HttpResponse(json.dumps(db.sendMessage(200, "Successfully deleted " + gid + " owned by " + uid + '.'), indent=4, separators=(',', ': ')), content_type="application/json")
            else:
                return HttpResponse(json.dumps(db.throwError(404, "You do not own any such Graph."), indent=4, separators=(',', ': ')), content_type="application/json")

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def setDefaultLayout(request):
    if request.method == 'POST':
        result = db.setDefaultLayout(request.POST['layoutId'], request.POST['gid'], request.POST['uid'])
        if result != None:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "Set " + request.POST['layoutId'] + " as default")), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def removeDefaultLayout(request):
    if request.method == 'POST':
        result = db.removeDefaultLayout(request.POST['layoutId'], request.POST['gid'], request.POST['uid'])
        if result != None:
            return HttpResponse(json.dumps(db.throwError(400, result)), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "Removed " + request.POST['layoutId'] + " as default")), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

def renderImage(request):
    # This is a temporary route so Allison's graphs show up
    return HttpResponseRedirect(URL_PATH + 'static/images/legend.png');

def shareLayoutWithGroups(request):
    '''
        Toggles shares/unshare graph with specified groups.

        :param request:Incoming HTTP POST Request containing:
        {"gid": <name of graph>, "owner": <owner of the graph>, "groups_to_share_with": [group_ids], "groups_not_to_share_with": [group_ids]}
        :return TBD
    '''
    if request.method == 'POST':
        layout_owner = request.POST['loggedIn']
        gid = request.POST['gid']
        uid = request.POST['uid']
        layoutId = request.POST['layoutId']
        current_user = request.session.get('uid')

        # If user is not logged on, they can't do anything
        if current_user == None:
            return HttpResponse(json.dumps(db.throwError(500, "Must be signed in to make share layouts!")), content_type="application/json")

        # If user is the owner of the graph or if they are the layout owner, can they share a layout
        if current_user != uid and db.get_layout_for_graph(layoutId, layout_owner, gid, uid, current_user) == None:
            return HttpResponse(json.dumps(db.throwError(500, "Not authorized to share layouts!")), content_type="application/json")

        if db.can_see_shared_graph(current_user, uid, gid) == None:
            return HttpResponse(json.dumps(db.throwError(500, "Not allowed to do this operation!")), content_type="application/json")
        
        if len(db.get_all_groups_for_this_graph(uid, gid)) == 0:
            return HttpResponse(json.dumps(db.throwError(400, "No groups to share with.  Either share this graph with a group first or make this graph public!")), content_type="application/json")
        else:
            if db.is_public_graph(uid, gid):
                db.makeLayoutPublic(uid, gid, layoutId, layout_owner)
            else:
                db.share_layout_with_all_groups_of_user(uid, gid, layoutId, layout_owner)
 
            return HttpResponse(json.dumps(db.sendMessage(200, "Okay")), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

##### END VIEWS #####

##### REST API #####

def graph_exists(request, user_id, graphname):
    '''
        Checks to see if a graph exists

        @param request: HTTP POST Request
        @param user_id: Owner of graph
        @param: graph_name: Name of graph
    '''
    if request.method == 'POST':

        if request.POST['username'] != user_id:
            return HttpResponse(json.dumps(db.usernameMismatchError(), indent=4, separators=(',', ': ')), content_type="application/json")

        if db.get_valid_user(user_id, request.POST['password']) == None:
            return HttpResponse(json.dumps(db.userNotFoundError(), indent=4, separators=(',', ': ')), content_type="application/json")

        graph_exists = db.graph_exists(user_id, graphname)

        if graph_exists == False:
            return HttpResponse(json.dumps(db.throwError(404, "User " + user_id + " owns no graph with id " + graphname + "!"), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps(db.sendMessage(200, "User " + user_id + " owns a graph with id " + graphname + "!"), indent=4, separators=(',', ': ')), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
            return HttpResponse(json.dumps(db.sendMessage(201, "Added " + graphname + " for " + user_id + '.'), indent=4, separators=(',', ': ')), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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

        data = db.get_all_groups_with_member(request.POST['username'])
        return HttpResponse(json.dumps({"StatusCode": 200, "Groups": data}, indent=4, separators=(',', ': ')), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
            if data != None:
                return HttpResponse(json.dumps(db.throwError(404, "Group not found!"), indent=4, separators=(',', ': ')), content_type="application/json")
            else:
                return HttpResponse(json.dumps(db.sendMessage(200, data), indent=4, separators=(',', ': ')), content_type="application/json");
        else:
            return HttpResponse(json.dumps(db.throwError(400, "The group owner and the person making this request are not the same person!"), indent=4, separators=(',', ': ')), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
        if result == None:
            return HttpResponse(json.dumps(db.sendMessage(404, "Graph does not exist!"), indent=4, separators=(',', ': ')), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"StatusCode": 200, "Tags": result}, indent=4, separators=(',', ': ')), content_type="application/json")
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

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
    else:
        context = {"Error": "This route only accepts POST requests."}
        return render(request, 'graphs/error.html', context)

# Private Utility methods used throughout views.py

def handler_404(request):
    if request.method == 'POST':
        return HttpResponse(json.dumps(db.throwError(404, "REST API endpoint does not exist!")), content_type="application/json")
    else:
        return render(request,'404.html')

def handler_500():
    if request.method == 'POST':
        return HttpResponse(json.dumps(db.throwError(500, "An error was encountered during this request.  REST API call not successful.")), content_type="application/json")
    else:
        return render(request,'500.html')

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
            context['message'] = "It appears that there are no public graphs available.  Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a>."
        elif search != None and tags == None:
            context['message'] = "It appears that there are no public graphs available that match the search criteria.  Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a> with the given search criteria."
        elif tags != None and search == None:
            context['message'] = "It appears that there are no public graphs available that match the tag criteria.  Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a> with the given tag criteria."
        else:
            context['message'] = "It appears that there are no public graphs available that match the search and tag criteria.  Please create an account and join a group or <a href='/../help/programmers/#add_graph'>upload</a> your own graphs with the given search and tag criteria."

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
            context['message'] = "It appears that you currently have no graphs uploaded. Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a>."
        elif search != None and tags == None:
            context['message'] = "It appears that you currently have no graphs uploaded that match the search terms. Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a> with the given search criteria in order to see them here."
        elif tags != None and search == None:
            context['message'] = "It appears that you currently have no graphs uploaded that match the tag terms. Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a> with the given tag criteria in order to see them here."
        else:
            context['message'] = "It appears that you currently have no graphs uploaded that match the serach and tag terms. Please create an account and join a group or upload your own graphs through the <a href='/../help/programmers/#add_graph'>REST API</a> or <a href='upload'>web interface</a>  with the given search and tag criteria in order to see them here."

    return context
