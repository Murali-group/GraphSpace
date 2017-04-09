"""migrate graph json to elastic search engine

Revision ID: 97a32c589371
Revises: 7df7ee83a212
Create Date: 2017-03-31 13:00:12.667770

"""
import json

from alembic import op
import sqlalchemy as sa
from elasticsearch import Elasticsearch
from graphspace.data_type import DataType


# revision identifiers, used by Alembic.
revision = '97a32c589371'
down_revision = '7df7ee83a212'
branch_labels = None
depends_on = None

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('graph_json', sa.String)
)


def map_attributes(attributes):

	mapped_attributes = {}
	if attributes and isinstance(attributes, dict) and DataType.forValue(attributes) == DataType.DICT:
		for key, value in attributes.items():
			value_type = DataType.forValue(value)
			key_prefix = value_type.prefix()
			mapped_key = key_prefix + key if not key.startswith(key_prefix) else key
			if value_type == DataType.DICT:
				mapped_attributes[mapped_key] = map_attributes(value)
			else:
				mapped_attributes[mapped_key] = DataType.dateToStr(value, value_type)
	elif attributes and isinstance(attributes, list) and DataType.forValue(attributes) == DataType.DICT:
		return [map_attributes(item) for item in attributes]

	return mapped_attributes


def jsonify_graph_jsonstring(graph_jsonstring):
	graph = json.loads(graph_jsonstring)
	if 'data' in graph:
		graph['data'] = {k: json.dumps(v) for k, v in graph['data'].items()}
	if 'elements' in graph and 'nodes' in graph['elements']:
		graph['nodes'] = [{
			'data': {k: json.dumps(v) for k, v in node['data'].items()}
		} for node in graph['elements']['nodes']]
	if 'elements' in graph and 'edges' in graph['elements']:
		graph['edges'] = [{
			'data': {k: json.dumps(v) for k, v in edge['data'].items()}
		} for edge in graph['elements']['edges']]
	return graph


def upgrade():
	es = Elasticsearch()
	connection = op.get_bind()
	es.indices.create(index='graphs', ignore=400)

	for graph in connection.execute(graphhelper.select()):
		es.index(index="graphs", doc_type="json", id=graph.id, body=map_attributes(json.loads(graph.graph_json)))
	pass


def downgrade():
	es = Elasticsearch()
	es.indices.delete(index='graphs', ignore=[400, 404])
