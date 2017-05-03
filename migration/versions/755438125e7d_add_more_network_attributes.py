"""add more network attributes

Revision ID: 755438125e7d
Revises: 97a32c589371
Create Date: 2017-04-12 23:55:47.368030

"""
from alembic import op
import sqlalchemy as sa

import json
from graphspace_python.graphs.classes.gsgraph import GSGraph
from graphspace_python.graphs.formatter.json_formatter import CyJSFormat
from graphspace_python.api.client import GraphSpace

# revision identifiers, used by Alembic.
revision = '755438125e7d'
down_revision = '97a32c589371'
branch_labels = None
depends_on = None


def upgrade():
	# graphspace = GraphSpace('adb@vt.edu', 'XXXX')
	# # graphspace.set_api_host('localhost:8000')
	# response = graphspace.get_public_graphs(limit=70)
	# for graph in response['graphs']:
	# 	graph_json = graph['graph_json']
	# 	G = CyJSFormat.create_gsgraph(json.dumps(graph['graph_json']))
	# 	tags = list(set(G.get_tags()) | set(graph['tags']))
	# 	G.set_tags(tags)
	#
	# 	if '2015-bioinformatics-xtalk' in tags:
	# 		G.set_data({
	# 			'pmid': '26400040',
	# 			'paper_title': 'Xtalk: a path-based approach for identifying crosstalk between signaling pathways.',
	# 			'authors': ['Allison N. Tegge', 'Nicholas Sharp', 'T. M. Murali']
	# 		})
	# 	elif '2013-jcb-linker' in tags:
	# 		G.set_data({
	# 			'pmid': '23641868',
	# 			'paper_title': 'Pathways on demand: automated reconstruction of human signaling networks.',
	# 			'organism': 'Saccharomyces cerevisiae',
	# 			'taxon_id': '559292',
	# 			'pubmed_authors': ['Christopher L. Poirel', 'Richard R. Rodrigues','Katherine C. Chen','John J. Tyson', 'T. M. Murali']
	# 		})
	# 	elif 'pathlinker-paper' in tags or '2015-npj-sysbio-appl-pathlinker' in tags:
	# 		G.set_data({
	# 			'paper_title': 'Top-down network analysis to drive bottom-up modeling of physiological processes.',
	# 			'organism': 'Homo sapiens',
	# 			'taxon_id': '9606',
	# 			'pubmed_authors': ['Anna Ritz', 'Christopher L Poirel', 'Allison N Tegge', 'Nicholas Sharp', 'Kelsey Simmons', 'Allison Powell', 'Shiv D Kale', 'T. M. Murali']
	# 		})
	# 	print(graph['id'])
	# 	response = graphspace.update_graph(graph['name'], owner_email=graph['owner_email'], graph=G, is_public=graph['is_public'])
	# raise
	pass


def downgrade():
	pass
