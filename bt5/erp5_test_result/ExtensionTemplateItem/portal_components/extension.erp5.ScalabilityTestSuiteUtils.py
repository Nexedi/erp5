##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company    return "OK"
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import jinja2
import json
from six.moves import range

def getGeneratedConfigurationList(self, *args, **kw):
  document_list = []
  template = jinja2.Template(self.getClusterConfiguration())
  max_ = len(self.getGraphCoordinate())
  max_comp = 100
  #max = self.getNumberConfiguration()
  comp_list_view = [ "COMP-%i" %(x) for x in range(0,max_comp) ]

  for count in range(1, max_+1):
    template_vars = { "count" : count, "comp" : comp_list_view }
    output_text = template.render(template_vars)
    description = json.dumps(json.loads(output_text), sort_keys=True, indent=4, separators=(',', ': '))

    # Create a temp object
    document_list.append(self.newContent(
      temp_object=1,
      title="%i" % count,
      description="%s" %(description)))

  return document_list




def generateConfigurationList(self, test_suite_title):
  """
  generateConfigurationList : generate a dict wich contains a list
  of cluster configurations for testnodes, using a test_suite and
  available testnodes.
  If it is not possible to generate a configuration, the 'launchable'
  entry is False, otherwise it is True.
  """
  def _unvalidateConfig(my_dict):
    my_dict['launchable'] = False
    if 'launcher_nodes_computer_guid' in my_dict:
      my_dict['launcher_nodes_computer_guid'] = {}
    if 'involved_nodes_computer_guid' in my_dict:
      my_dict['involved_nodes_computer_guid'] = {}
    if 'configuration_list' in my_dict:
      my_dict['configuration_list'] = []


  def _isInMyDictOrListRec(my_container, my_value):
    def _isInMyDictOrList(current_container):
      if current_container == my_value :
        return True
      elif isinstance(current_container, dict):
        for v in current_container.values():
          if _isInMyDictOrList(v) :
            return True
      elif isinstance(current_container, list):
        for sub_container in current_container:
          if _isInMyDictOrList(sub_container) :
            return True
      # Not found at this level and below
      return False
    return _isInMyDictOrList(my_container)



  portal = self.getPortalObject()
  test_suite_module = portal.test_suite_module
  test_node_module = portal.test_node_module
  portal_task_distribution = portal.portal_task_distribution
  # Get test_suite informations from his title given in parameter
  test_suite = test_suite_module.searchFolder(title=test_suite_title)[0]
  lll = portal_task_distribution.searchFolder(title=test_suite.getSpecialiseTitle())
  distributor_uid = lll[0].getUid()
  cluster_configuration = test_suite.getClusterConfiguration()
  number_configuration = len(test_suite.getGraphCoordinate())
  randomized_path = test_suite.getRandomizedPath()
  # Get testnodes available for this distributor

  unvalid_node = "_my_unvalidated_dummy_node"
  # Validated nodes wich are available to run test
  available_nodes = test_node_module.searchFolder(
          portal_type="Test Node", validation_state="validated",
          specialise_uid=distributor_uid)
  # Remaining node are nodes that can be insert in the template (so, excluded launcher nodes)
  remaining_nodes = list(available_nodes)
  launcher_nodes = []
  launcher_nodes.append( remaining_nodes.pop() )

  # Make list with only the computer_guid property of each node (to be used directly by template)
  remaining_nodes_computer_guid = [unvalid_node] + [ node.getReference() for node in remaining_nodes ] + [unvalid_node]
  launcher_nodes_computer_guid = [ node.getReference() for node in launcher_nodes ]

  configuration_list_json = []
  return_dict = {}
  return_dict['error_message'] = 'No error.'
  return_dict['randomized_path'] = randomized_path
  # Will be modified after
  return_dict['launchable'] = False

  # source of possible error :
  # bad json configuration
  try:
    template = jinja2.Template(cluster_configuration)
    for count in range(1, number_configuration+1):
      template_vars = { "count" : count, "comp" : remaining_nodes_computer_guid }
      configuration_list_json.append( json.loads( template.render( template_vars ) ) )
    return_dict['launchable'] = True
    return_dict['configuration_list'] = configuration_list_json
    return_dict['launcher_nodes_computer_guid'] = launcher_nodes_computer_guid
  except Exception as e:
    return_dict['error_message'] = 'Bad json cluster_configuration. %s' % str(e)
    _unvalidateConfig(return_dict)

  # If the number of available nodes is lower than
  # the number of nodes required by the template
  if _isInMyDictOrListRec(return_dict, unvalid_node):
    _unvalidateConfig(return_dict)
    return_dict['error_message'] = 'The number of testnodes available for running\
 the current test (%s) is insufficient.' %(test_suite_title)

  # Get the list of all nodes wich will are involved in the test
  involved_nodes_computer_guid = []
  for node in available_nodes:
    computer_guid = node.getReference()
    if _isInMyDictOrListRec(return_dict, computer_guid):
      involved_nodes_computer_guid.append(computer_guid)

  return_dict['involved_nodes_computer_guid'] = involved_nodes_computer_guid
  return return_dict