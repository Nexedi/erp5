##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import six
try:
  import pydot
except ImportError:
  pydot = None


def ERP5Site_getGraphEditorGraphLayout(self, graph_editor_dict):
  if pydot is None:
    return dict(node=dict())
  graph = pydot.Dot()

  for node_id in graph_editor_dict['node']:
    graph.add_node(pydot.Node(node_id))
  for edge in six.itervalues(graph_editor_dict['edge']):
    graph.add_edge(pydot.Edge(
      edge['source'],
      edge['destination'],
    ))

  new_graph, = pydot.graph_from_dot_data(graph.create_dot().decode())  # pylint:disable=unpacking-non-sequence

  # calulate the ratio from the size of the bounding box
  origin_left, origin_top, max_left, max_top = [
    float(p) for p in new_graph.get_bb().strip('"').split(',')
  ]
  ratio_top = max_top - origin_top
  ratio_left = max_left - origin_left

  node_position_dict = dict()
  for node in new_graph.get_nodes():
    # skip technical nodes (and \n bug on py3)
    if node.get_name() in ('graph', 'node', 'edge', '"\\n"'):
      continue
    left, top = [float(p) for p in node.get_pos()[1:-1].split(",")]
    node_position_dict[node.get_name().strip('"')] = dict(
      coordinate=dict(
        top=1 - (top / ratio_top),
        left=1 - (left / ratio_left),
      ))

  return dict(node=node_position_dict)
