"""migrate graph json to elastic search engine

Revision ID: 97a32c589371
Revises: 67bfd4a0665b
Create Date: 2017-03-31 13:00:12.667770

"""
import json

from alembic import op
import sqlalchemy as sa
from elasticsearch import Elasticsearch
from graphspace.data_type import DataType


# revision identifiers, used by Alembic.
revision = '97a32c589371'
# down_revision = '7df7ee83a212'
down_revision = '67bfd4a0665b'
branch_labels = None
depends_on = None

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('graph_json', sa.String)
)

template = "{\"template\":\"graphs\",\"order\":0,\"settings\":{\"index\":{\"refresh_interval\":\"30s\",\"analysis\":{\"analyzer\":{\"my_analyzer\":{\"type\":\"custom\",\"tokenizer\":\"my_ngram_tokenizer\",\"filter\":[\"lowercase\",\"my_ngram_filter\"]}},\"filter\":{\"my_ngram_filter\":{\"type\":\"nGram\",\"max_gram\":15,\"min_gram\":2}},\"tokenizer\":{\"my_ngram_tokenizer\":{\"type\":\"nGram\",\"min_gram\":2,\"max_gram\":15,\"token_chars\":[\"letter\",\"digit\",\"punctuation\"]}}}}},\"mappings\":{\"json\":{\"date_detection\":false,\"_all\":{\"enabled\":false},\"dynamic_templates\":[{\"default_string_mapping\":{\"match\":\"*\",\"match_mapping_type\":\"string\",\"mapping\":{\"type\":\"string\"}}},{\"geopoint_mapping\":{\"mapping\":{\"geohash_precision\":\"1km\",\"type\":\"geo_point\",\"doc_values\":true,\"geohash_prefix\":true,\"lat_lon\":true,\"fielddata\":{\"precision\":\"10m\",\"format\":\"compressed\"}},\"match\":\"geopoint_*\"}},{\"string_mapping\":{\"match\":\"string_*\",\"mapping\":{\"type\":\"string\",\"analyzer\":\"my_analyzer\",\"fields\":{\"raw\":{\"type\":\"string\",\"index\":\"not_analyzed\"}}}}},{\"bool_mapping\":{\"match\":\"bool_*\",\"mapping\":{\"type\":\"boolean\"}}},{\"datetime_mapping\":{\"match\":\"datetime_*\",\"mapping\":{\"type\":\"date\"}}},{\"long_mapping\":{\"match\":\"long_*\",\"mapping\":{\"type\":\"long\"}}},{\"double_mapping\":{\"match\":\"double_*\",\"mapping\":{\"type\":\"double\"}}}]}}}"

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
	es.indices.delete(index='graphs', ignore=[400, 404])
	es.indices.create(index='graphs', ignore=400)
	es.indices.put_template(name='template_common', body=json.loads(template))
	total = connection.execute(graphhelper.select()).rowcount
	offset = 0
	while offset < total:
		for graph in connection.execute(graphhelper.select().order_by("id").limit(100).offset(offset)):
			print(graph.id)
			es.index(index="graphs", doc_type="json", id=graph.id, body=map_attributes(json.loads(graph.graph_json)))
		offset += 100
	pass


def downgrade():
	es = Elasticsearch()
	es.indices.delete(index='graphs', ignore=[400, 404])
	pass
