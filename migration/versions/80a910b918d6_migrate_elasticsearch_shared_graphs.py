"""migrate elasticsearch shared graphs

Revision ID: 80a910b918d6
Revises: bb9a45e2ee5e
Create Date: 2021-03-27 13:14:53.551264

"""
from alembic import op
import json
import sqlalchemy as sa
from sqlalchemy import create_engine, ForeignKey
from elasticsearch import Elasticsearch
from graphspace.data_type import DataType
import requests


# revision identifiers, used by Alembic.
revision = '80a910b918d6'
down_revision = 'bb9a45e2ee5e'
branch_labels = None
depends_on = None

"""
	This migration scripts modifies the data that is put into elasticsearch.
	The following is the JSON structure of the _source object in Elasticsearch - 

	"_source": {
		"string_owner_email": "jeffl@vt.edu",
        "long_shared_users": [
            38,
            84,
            114,
        ],
        "datetime_updated_at": "2017-10-24T19:48:28.839888",
        "long_is_public": 1
	}

	Note: The new fields added are
		string_owner_email from owner_email field in postgres
		datetime_updated_at from updated_at field in postgres
		long_is_public from is_public field in postgres
		long_shared_users comes from the intersection of GroupToGraph and GroupToUser

	The graph_id and group_id are retrieved from group_to_graph_helper
	The group_id and user_id are retrieved from group_to_user_helper
	Using this we get a list of users each graph is shared with and then store it in an array called long_shared_users.
"""

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('owner_email', sa.String),
	sa.Column('is_public', sa.Integer),
	sa.Column('updated_at', sa.DateTime),
	sa.Column('graph_json', sa.String)
)

group_to_graph_helper = sa.Table(
    'group_to_graph',
    sa.MetaData(),
    sa.Column('graph_id', sa.Integer),
    sa.Column('group_id', sa.Integer, primary_key=True)
)

group_to_user_helper = sa.Table(
    'group_to_user',
    sa.MetaData(),
    sa.Column('group_id', sa.Integer, ForeignKey(group_to_graph_helper.c.group_id)),
    sa.Column('user_id', sa.Integer)
)

template = '{\"template\": \"graphs\",\"order\": 0,\"settings\": {\"index\": {\"refresh_interval\": \"30s\",\"analysis\": {\"normalizer\": {\"case_insensitive_normalizer\": {\"type\": \"custom\",\"filter\": [\"lowercase\",\"asciifolding\"]}},\"analyzer\": {\"my_analyzer\": {\"type\": \"custom\",\"tokenizer\": \"my_ngram_tokenizer\",\"filter\": [\"lowercase\",\"my_ngram_filter\"]}},\"filter\": {\"my_ngram_filter\": {\"type\": \"nGram\",\"max_gram\": 15,\"min_gram\": 2}},\"tokenizer\": {\"my_ngram_tokenizer\": {\"type\": \"nGram\",\"min_gram\": 2,\"max_gram\": 15,\"token_chars\": [\"letter\",\"digit\",\"punctuation\"]}}}}},\"mappings\": {\"json\": {\"date_detection\": true,\"_all\": {\"enabled\": false},\"dynamic_templates\": [{\"default_string_mapping\": {\"match\": \"*\",\"match_mapping_type\": \"string\",\"mapping\": {\"type\": \"string\"}}},{\"geopoint_mapping\": {\"mapping\": {\"geohash_precision\": \"1km\",\"type\": \"geo_point\",\"doc_values\": true,\"geohash_prefix\": true,\"lat_lon\": true,\"fielddata\": {\"precision\": \"10m\",\"format\": \"compressed\"}},\"match\": \"geopoint_*\"}},{\"string_mapping\": {\"match\": \"string_*\",\"mapping\": {\"type\": \"string\",\"analyzer\": \"my_analyzer\",\"fields\": {\"raw\": {\"type\": \"string\",\"index\": \"not_analyzed\"}}}}},{\"bool_mapping\": {\"match\": \"bool_*\",\"mapping\": {\"type\": \"boolean\"}}},{\"datetime_mapping\": {\"match\": \"datetime_*\",\"mapping\": {\"type\": \"date\"}}},{\"long_mapping\": {\"match\": \"long_*\",\"mapping\": {\"type\": \"long\"}}},{\"double_mapping\": {\"match\": \"double_*\",\"mapping\": {\"type\": \"double\"}}}],\"properties\": {\"string_owner_email\": {\"type\": \"text\",\"fields\": {\"keyword\": {\"type\": \"keyword\", \"normalizer\":\"case_insensitive_normalizer\"}}},\"object_data\": {\"properties\": {\"string_name\": {\"type\": \"text\",\"fields\": {\"keyword\": {\"type\": \"keyword\", \"normalizer\":\"case_insensitive_normalizer\"}}}}}}}}}'


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
    print('starting')
    es = Elasticsearch()
    connection = op.get_bind()
    print(connection)

    es.indices.delete(index='graphs', ignore=[400, 404])
    print('deleted graphs')
    es.indices.create(index='graphs', ignore=400)
    print('created graphs')
    es.indices.put_template(name='template_common', body=json.loads(template))
    print('put template')

    #todo: change number respective to number of graphs
    total = 28299
    #total = connection.execute(graphhelper.select()).rowcount
    print('There are this many graphs to migrate: ', total)
    offset = 0
    count = 1

    graph_to_user = group_to_graph_helper.join(group_to_user_helper)

    updateLimitFields()

    while offset < total:
        print "offset: ", offset
        for graph in connection.execute(graphhelper.select().order_by("id").limit(50).offset(offset)):
            print "count: ", count, "\tGraph_id: ", graph.id
            body_data = map_attributes(json.loads(graph.graph_json))
            #print(body_data)
            body_data["string_owner_email"] = graph.owner_email
            body_data["long_is_public"] = graph.is_public
            body_data["datetime_updated_at"] = graph.updated_at
            users = [g.user_id for g in connection.execute(graph_to_user.select(group_to_graph_helper.c.graph_id == graph.id).order_by("graph_id"))]
            body_data["long_shared_users"] = users
            try:
                es.index(index="graphs", doc_type="json", id=graph.id, body=body_data, request_timeout=60)
            except ValueError:
                print('Could not index graph:', graph.id)
            count += 1
        offset += 50
    pass


def downgrade():
    es = Elasticsearch()
    es.indices.delete(index='graphs', ignore=[400, 404])
    pass

def updateLimitFields():
    print(requests.get("http://localhost:9200/graphs/_settings").text, "\n")
    headers = {'Content-Type': 'application/json'}
    payload = '{"index.mapping.total_fields.limit": 10000}'
    print(requests.put("http://localhost:9200/graphs/_settings", data=payload, headers=headers).text)
    print ("updated elasticsearch limit of fields to accomodate the migration")

