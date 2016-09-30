import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from applications.graphs.forms import SearchForm
import applications.graphs.controllers as graphs
import graphspace.utils as utils
from graphs.util.json_validator import convert_json


def search(request):
	"""
		Render the My Graphs page

		:param request: HTTP GET Request
	"""

	return _graphs_page(request, 'my graphs')


def shared_graphs(request):
	"""
		Render the graphs/shared/ page showing all graphs that are shared with a user

		:param request: HTTP GET Request
	"""

	return _graphs_page(request, 'shared')


def public_graphs(request):
	"""
		Render the graphs/public/ page showing all graphs that are public

		:param request: HTTP GET Request
	"""

	return _graphs_page(request, 'public')


def _graphs_page(request, view_type):
	"""
		wrapper view for the following pages:
			graphs/
			graphs/shared/
			graphs/public/

		:param request: HTTP GET Request
		:param view_type: Type of view for graph (Ex: my graphs, shared, public)
	"""
	context = RequestContext(request)
	graph_list = None  # List of graphs that will be returned by the request
	context['view_type'] = view_type  # Send view_type to front end to tell the user (through button color) where they are

	# # If there is an error, display the error
	# if context['Error']:
	# 	return render(request, 'graphs/error.html', context)

	uid = request.session['uid'] if 'uid' in request.session else None  # Checks to see if a user is currently logged on

	# Partial search may be thought of as "contains" matching
	# Exact search may be though of as "identical" matching
	context['search_type'] = None
	if 'partial_search' in request.GET:
		context['search_type'] = 'partial_search'
	elif 'full_search' in request.GET:
		context['search_type'] = 'full_search'

	context['tags'] = _clean_tag_query(request.GET.get('tags'))
	context['tag_terms'] = context['tags'].split(',')
	context['search_word'] = _clean_tag_query(request.GET.get(context['search_type']))
	context['search_word_terms'] = context['search_word'].split(',')
	# context['order_by'] = 'modified_descending' if len(request.GET.get('order').strip()) == 0 else request.GET.get('order').strip()
	context['order_by'] = 'modified_descending'

	context['page'] = 0
	# context['page'] = request.GET.get('page')
	context['page_size'] = 10

	if len(context['search_word_terms']) > 0:
		context['search_result'] = True

	context['my_graphs'] = graphs.search_graphs_owned_by_user(request, uid, context['search_type'], context['search_word_terms'], context['tag_terms'], context['order_by'], context['page'], context['page_size'])
	print(context['my_graphs'])
	# context['shared_graphs'] = graphs.search_graphs_shared_with_user(request, uid, context['search_type'], context['search_word_terms'], context['tag_terms'], context['order_by'], context['page'], context['page_size'])
	# context['public_graphs'] = graphs.search_public_graphs(request, uid, context['search_type'], context['search_word_terms'], context['tag_terms'], context['order_by'], context['page'], context['page_size'])
	context['search_form'] = SearchForm(placeholder='Search...')

	return HttpResponse(json.dumps(context), content_type="application/json")


def upload_graph_through_ui(request):
	context = RequestContext(request)

	if request.method == 'POST':
			title_of_graph = request.POST['title'] if 'title' in request.POST else None
			username = None if request.POST['email'] == 'Public User' else request.POST['email']
			try:
				if str(request.FILES['graphname']).endswith("json"):
					graph = graphs.uploadJSONFile(request, username, request.FILES['graphname'].read(), title_of_graph)
				else:
					graph = graphs.uploadCyjsFile(request, username, request.FILES['graphname'].read(), title_of_graph)

				context['Success'] = settings.URL_PATH + "graphs/" + graph.owner_email + "/" + graph.name
			except Exception as e:
				context['Error'] = str(e)

			return render(request, 'graphs/upload_graph.html', context)
	else:
		return render(request, 'graphs/upload_graph.html', context)


def _clean_tag_query(tag_query):
	if tag_query is None:
		return ''
	else:
		return ','.join([x for x in tag_query.split(',') if len(x.strip()) != 0])


def _clean_search_query(search_query):
	if search_query is None:
		return ''
	else:
		return ','.join([x for x in search_query.split(',') if len(x.strip()) != 0])


def view_graph(request, graph_owner, graphname):
	"""
		View a graph with CytoscapeJS.

		:param request: HTTP GET Request
		:param graph_owner: Owner of the graph to view
		:param graphname: Graph name of the graph to view
	"""
	context = RequestContext(request)
	graphname = graphname.strip('/')
	layoutname = request.GET.get('layout') if len(request.GET.get('layout', '')) > 0 else None
	layout_owner = request.GET.get('layout_owner') if len(request.GET.get('layout_owner', '')) > 0 else None

	try:
		graph = graphs.get_graph(request, graph_owner, graphname)

		if graph is None:
			raise Exception("Graph: " + graphname + " does not exist for " + graph_owner + ".  Upload a graph with this name into GraphSpace in order to see it.")

		if not graphs.is_user_authorized_to_view_graph(request, request.session['uid'], graph.id):
			raise Exception("You are not authorized to view this graph, create an account and contact graph's owner for permission to see this graph.")

		layout = graphs.get_layout(request, layout_owner, layoutname, graph.id)

		if layout is None:
			if "layout" in request.GET and layoutname not in graphs.AUTOMATIC_LAYOUT_ALGORITHMS:
				raise Exception("Layout: " + request.GET.get('layout') + " does not exist.  Click <a href='" + settings.URL_PATH + "graphs/" + graph_owner + "/" + graphname + "'>here</a> to view this graph without the specified layout.")
		elif layout.is_public !=1 and layout.is_shared !=1:
			raise Exception(layout.owner_email + " has not shared " + request.GET.get('layout') + " layout yet.  Click <a href='" + settings.URL_PATH + "graphs/" + graph_owner + "/" + graphname + "'>here</a> to view this graph without the specified layout.")
		else:
			context['default_layout_name'] = graph.default_layout.name
			context['default_layout'] = utils.cytoscapePresetLayout(json.dump(graph.default_layout.json))
			context['layout_name'] = layout.name
			context['layout_to_view'] = utils.cytoscapePresetLayout(json.dump(layout.json))
			context['layout_urls'] = settings.URL_PATH + "graphs/" + graph_owner + "/" + graphname + "?layout="
			context["layout_owner"] = layout.owner_email

			# If user is logged in, display my layouts and shared layouts
			if request.session['uid'] is not None:

				context['my_layouts'] = []
				context['shared_layouts'] = graph.layouts
				context['my_shared_layouts'] = []

				for layout in graph.layouts:
					if layout.is_shared_with_groups == 0 and layout.is_public == 0:
						context['my_layouts'].append(layout)
						context['my_shared_layouts'].append(layout)

		context["graph"] = _convert_to_cytoscape_json(graph.json)
		context['draw_graph'] = True
		context['shared_groups'] = [(group.name, group.owner_email) for group in graph.groups]
		context['shared'] = 'Publicly Shared' if graph.is_public else 'Privately Shared'

		json_data = json.loads(context['graph'])
		if 'description' in json_data['metadata']:
			context['description'] = json_data['metadata']['description'] + "</table></html>"
		else:
			context['description'] = ""

		context['owner'] = graph_owner

		# If the metadata has either a name or a title (backward-compatible)
		# display it on the top of the graph
		if 'name' in json_data['metadata']:
			context['graph_name'] = json_data['metadata']['name']
		elif 'title' in json_data['metadata']:
			context['graph_name'] = json_data['metadata']['title']
		else:
			context['graph_name'] = ''

		# graph id
		context['graph_id'] = graphname

		if len(json_data['graph']['edges']) > 0 and 'k' in json_data['graph']['edges'][0]['data']:
			context['filters'] = True

		# redirect if the user wishes to view the json data
		if request.method == "GET" and 'view_json' in request.GET:
			return HttpResponseRedirect("/json/%s/%s" % (graph_owner, graphname))

		context['draw_graph'] = True
		# Don't display the task_view
		context["task_view"] = False
		context["approve_view"] = False
		context["researcher_view"] = True

		return render(request, 'graphs/view_graph.html', context)

	except Exception as e:
		context['Error'] = str(e)
		return render(request, 'graphs/error.html', context)


def _convert_to_cytoscape_json(graphjson):
	"""
		Converts JSON to CytoscapeJS standards

		:param graphjson: JSON of graph to render on CytoscapeJS
		:return JSON: CytoscapeJS-compatible graphname
	"""

	temp_json = json.loads(graphjson)['graph']

	# for Cytoscape.js, if data is in properties, then we need to convert (main difference)
	if 'data' in temp_json:
		return convert_json(graphjson)
	else:
		return graphjson

