from graphs.models import share_graph_event
from django.test import TestCase
from db import (get_all_share_graph_event, get_share_graph_event_by_id,
	            get_share_graph_event_by_member_id, delete_share_graph_event,
	            update_share_graph_event, add_share_graph_event)


class share_graph_event_test(TestCase):
	def basic_test(self):
		share_event = add_share_graph_event()
		# add tests after adding logic

