import base64

import requests
import six
import urllib


class GraphSpace:
	API_HOST = 'localhost:8000'

	def __init__(self, username, password):
		self.auth_token = 'Basic %s' % base64.b64encode('{0}:{1}'.format(username, password))
		self.username = username

	def _make_request(self, method, path, url_params={}, data={}, headers=None):
		if headers is None:
			headers = {
				'Accept': 'application/json',
				'Content-Type': 'application/json',
				'Authorization': self.auth_token
			}

		if method == "GET":
			return requests.get('http://{0}{1}?{2}'.format(
				GraphSpace.API_HOST,
				six.moves.urllib.parse.quote(path.encode('utf-8')),
				urllib.urlencode(url_params)
			), headers=headers)
		elif method == "POST":
			return requests.post('http://{0}{1}?{2}'.format(
				GraphSpace.API_HOST,
				six.moves.urllib.parse.quote(path.encode('utf-8')),
				urllib.urlencode(url_params)
			), json=data, headers=headers)
		elif method == "PUT":
			return requests.put('http://{0}{1}?{2}'.format(
				GraphSpace.API_HOST,
				six.moves.urllib.parse.quote(path.encode('utf-8')),
				urllib.urlencode(url_params)
			), json=data, headers=headers)
		elif method == "DELETE":
			return requests.delete('http://{0}{1}?{2}'.format(
				GraphSpace.API_HOST,
				six.moves.urllib.parse.quote(path.encode('utf-8')),
				urllib.urlencode(url_params)
			), headers=headers)

	def post_graph(self, graph, is_public=0):
		"""
		Posts NetworkX graph with name 'graph_name' to the account of the user 'owner_email' to GraphSpace.

		Parameters
		----------
		graph
		graph_name
		is_public

		Returns
		-------
		JSON response

		"""

		return self._make_request("POST", '/api/v1/graphs/',
								  data={
									  'name': graph.get_name(),
									  'is_public': 0 if is_public is None else is_public,
									  'owner_email': self.username,
									  'graph_json': graph.compute_graph_json(),
									  'style_json': graph.get_style_json()
								  }).json()

	def get_graph(self, graph_id):
		return self._make_request("GET", '/api/v1/graphs/' + str(graph_id)).json()

	def get_graphs(self):
		return self._make_request("GET", '/api/v1/graphs/').json()

	def delete_graph(self, graph_id):
		return self._make_request("DELETE", '/api/v1/graphs/' + str(graph_id)).json()

	def update_graph(self, graph_id, graph=None, is_public=0):
		if graph is not None:
			data = {
				'name': graph.get_name(),
				'is_public': 0 if is_public is None else is_public,
				'owner_email': self.username,
				'json': graph.compute_json()
			}
		else:
			data = {}

		return self._make_request("PUT", '/api/v1/graphs/' + str(graph_id), data=data).json()

	def make_graph_public(self, graph_id):
		return self._make_request("PUT", '/api/v1/graphs/' + str(graph_id), data={'is_public': 1}).json()
