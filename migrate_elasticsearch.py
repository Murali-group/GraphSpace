import json

import sqlalchemy as sa
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch
from graphspace.data_type import DataType


graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('owner_email', sa.String),
	sa.Column('is_public', sa.Integer),
	sa.Column('updated_at', sa.DateTime),
	sa.Column('graph_json', sa.String)
)

template = '{\"template\": \"graphs\",\"order\": 0,\"settings\": {\"index\": {\"refresh_interval\": \"30s\",\"analysis\": {\"analyzer\": {\"my_analyzer\": {\"type\": \"custom\",\"tokenizer\": \"my_ngram_tokenizer\",\"filter\": [\"lowercase\",\"my_ngram_filter\"]}},\"filter\": {\"my_ngram_filter\": {\"type\": \"nGram\",\"max_gram\": 15,\"min_gram\": 2}},\"tokenizer\": {\"my_ngram_tokenizer\": {\"type\": \"nGram\",\"min_gram\": 2,\"max_gram\": 15,\"token_chars\": [\"letter\",\"digit\",\"punctuation\"]}}}}},\"mappings\": {\"json\": {\"date_detection\": true,\"_all\": {\"enabled\": false},\"dynamic_templates\": [{\"default_string_mapping\": {\"match\": \"*\",\"match_mapping_type\": \"string\",\"mapping\": {\"type\": \"string\"}}},{\"geopoint_mapping\": {\"mapping\": {\"geohash_precision\": \"1km\",\"type\": \"geo_point\",\"doc_values\": true,\"geohash_prefix\": true,\"lat_lon\": true,\"fielddata\": {\"precision\": \"10m\",\"format\": \"compressed\"}},\"match\": \"geopoint_*\"}},{\"string_mapping\": {\"match\": \"string_*\",\"mapping\": {\"type\": \"string\",\"analyzer\": \"my_analyzer\",\"fields\": {\"raw\": {\"type\": \"string\",\"index\": \"not_analyzed\"}}}}},{\"bool_mapping\": {\"match\": \"bool_*\",\"mapping\": {\"type\": \"boolean\"}}},{\"datetime_mapping\": {\"match\": \"datetime_*\",\"mapping\": {\"type\": \"date\"}}},{\"long_mapping\": {\"match\": \"long_*\",\"mapping\": {\"type\": \"long\"}}},{\"double_mapping\": {\"match\": \"double_*\",\"mapping\": {\"type\": \"double\"}}}],\"properties\": {\"string_owner_email\": {\"type\": \"text\",\"fields\": {\"keyword\": {\"type\": \"keyword\"}}},\"object_data\": {\"properties\": {\"string_name\": {\"type\": \"text\",\"fields\": {\"keyword\": {\"type\": \"keyword\"}}}}}}}}}'
#template = "{\"template\":\"graphs1\",\"order\":0,\"settings\":{\"index\":{\"refresh_interval\":\"30s\",\"analysis\":{\"analyzer\":{\"my_analyzer\":{\"type\":\"custom\",\"tokenizer\":\"my_ngram_tokenizer\",\"filter\":[\"lowercase\",\"my_ngram_filter\"]}},\"filter\":{\"my_ngram_filter\":{\"type\":\"nGram\",\"max_gram\":15,\"min_gram\":2}},\"tokenizer\":{\"my_ngram_tokenizer\":{\"type\":\"nGram\",\"min_gram\":2,\"max_gram\":15,\"token_chars\":[\"letter\",\"digit\",\"punctuation\"]}}}}},\"mappings\":{\"json\":{\"include_in_all\": false, \"properties\": {\"object_elements\": {\"properties\":{\"object_nodes\":{\"properties\":{\"object_data\":{\"properties\":{\"string_name\":{\"type\": \"text\", \"include_in_all\": true}, \"string_label\":{\"type\": \"text\", \"include_in_all\": true}, \"string_aliases\":{\"type\": \"text\", \"include_in_all\": true}}}}}}}}, \"date_detection\":false,\"_all\":{\"enabled\":true},\"dynamic_templates\":[{\"default_string_mapping\":{\"match\":\"*\",\"match_mapping_type\":\"string\",\"mapping\":{\"type\":\"string\"}}},{\"geopoint_mapping\":{\"mapping\":{\"geohash_precision\":\"1km\",\"type\":\"geo_point\",\"doc_values\":true,\"geohash_prefix\":true,\"lat_lon\":true,\"fielddata\":{\"precision\":\"10m\",\"format\":\"compressed\"}},\"match\":\"geopoint_*\"}},{\"string_mapping\":{\"match\":\"string_*\",\"mapping\":{\"type\":\"string\",\"analyzer\":\"my_analyzer\",\"fields\":{\"raw\":{\"type\":\"string\",\"index\":\"not_analyzed\"}}}}},{\"bool_mapping\":{\"match\":\"bool_*\",\"mapping\":{\"type\":\"boolean\"}}},{\"datetime_mapping\":{\"match\":\"datetime_*\",\"mapping\":{\"type\":\"date\"}}},{\"long_mapping\":{\"match\":\"long_*\",\"mapping\":{\"type\":\"long\"}}},{\"double_mapping\":{\"match\":\"double_*\",\"mapping\":{\"type\":\"double\"}}}]}}}"

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


def migrate():
	es = Elasticsearch()
	connection = create_engine(''.join(
			['postgresql://', 'postgres', ':', 'test', '@', 'localhost', ':', '5432', '/', 'gsdb']), echo=False).connect()

	print(connection)

	es.indices.delete(index='graphs', ignore=[400, 404])
	es.indices.create(index='graphs', ignore=400)
	es.indices.put_template(name='template_common', body=json.loads(template))
	
	total = 22118

	offset = 0
	while offset < total:
		for graph in connection.execute(graphhelper.select().order_by("id").limit(30).offset(offset)):
			print(graph.id)
			body_data = map_attributes(json.loads(graph.graph_json))
			body_data["string_owner_email"] = graph.owner_email
			body_data["long_is_public"] = graph.is_public
			body_data["datetime_updated_at"] = graph.updated_at
			es.index(index="graphs", doc_type="json", id=graph.id, body=body_data)
		offset += 30
	connection.close()
	pass


migrate()


'''
	wnt
		Old Code and 10 size : 0.5838
		*node* and 10 size : 0.058
			Speedup: 90.06 %
		_all and 10 size : 0.056
			Speedup: 90.40 %

	p53
		Old Code and 10 size : 3.7055
		*node* and 10 size : 0.681
			Speedup:  81.62 %
		_all and 10 size : 0.668
			Speedup: 81.97 %
	
	kegg
		Old Code and 10 size : 0.256
		*node* and 10 size : 0.106
			Speedup: 58.59 %
		_all and 10 size : 0.096
			Speedup: 62.5 %

	path
		Old Code and 10 size : 2.92
		*node* and 10 size : 0.149
			Speedup: 94.89 %
		_all and 10 size : 0.13
			Speedup: 95.54 %

	pathway
		Old Code and 10 size : 0.683
		*node* and 10 size : 0.144
			Speedup: 78.91 %
		_all and 10 size : 0.12
			Speedup: 82.43 %

	ab
		Old Code and 10 size : 3.10
		*node* and 10 size : 1.28
			Speedup: 58.71 %
		_all and 10 size : 0.93
			Speedup: 70%                                                                   

'''