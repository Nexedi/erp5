# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from App.config import getConfiguration
import shutil
import os
import tempfile
from Products.ERP5.genbt5list import generateInformation
from zLOG import LOG
from Products.ERP5.Document.BusinessTemplate import PortalTypeWorkflowChainTemplateItem
from copy import deepcopy
from lxml.etree import parse
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5.genbt5list import main as genbt5list


def _old_portal_type_workflow_chain_template_item_preinstall(self, context, installed_item, **kw):
  '''
    version of PortalTypeWorkflowChainTemplateItem.preinstall 
    copied from 8229186069c17a5454e024e1e664e2871b7f1576
  '''
  modified_object_list = {}
  new_dict = PersistentMapping()
  # Fix key from installed bt if necessary
  for key, value in installed_item._objects.iteritems():
    if not 'portal_type_workflow_chain/' in key:
      key = 'portal_type_workflow_chain/%s' % (key)
    new_dict[key] = value
  if new_dict:
    installed_item._objects = new_dict
  for path in self._objects:
    if path in installed_item._objects:
      # compare object to see it there is changes
      new_object = self._objects[path]
      old_object = installed_item._objects[path]
      if isinstance(new_object, str):
        new_object = new_object.split(self._chain_string_separator)
      if isinstance(old_object, str):
        old_object = old_object.split(self._chain_string_separator)
      new_object.sort()
      old_object.sort()
      if new_object != old_object:
        modified_object_list.update({path : ['Modified', self.getTemplateTypeName()]})
    else: # new object
      modified_object_list.update({path : ['New', self.getTemplateTypeName()]})
  # get removed object
  for path in installed_item._objects:
    if path not in self._objects:
      modified_object_list.update({path : ['Removed', self.getTemplateTypeName()]})
  return modified_object_list

def _old_portal_type_workflow_chain_template_item_importFile(self, file_name, file):
  '''
    version of PortalTypeWorkflowChainTemplateItem._importFile 
    copied from 8229186069c17a5454e024e1e664e2871b7f1576
  '''
  if not file_name.endswith('.xml'):
    LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
    return
  # import workflow chain for portal_type
  result_dict = {}
  xml = parse(file)
  chain_list = xml.findall('chain')
  for chain in chain_list:
    portal_type = chain.find('type').text
    workflow_chain = chain.find('workflow').text or ''
    if 'portal_type_workflow_chain/' not in portal_type:
      key = 'portal_type_workflow_chain/%s' % (portal_type,)
    else:
      key = portal_type
    result_dict[key] = workflow_chain.split(self._chain_string_separator)
  self._objects = result_dict

class TestBusinessTemplateCompatibilityWithPreviouslyInstalledVersion(ERP5TypeTestCase):

  def test_compatibility_on_portal_type_workflow_chain_template_item(self):
    current_preinstall = deepcopy(PortalTypeWorkflowChainTemplateItem.preinstall)
    current_importFile = deepcopy(PortalTypeWorkflowChainTemplateItem.importFile)
    old_preinstall = _old_portal_type_workflow_chain_template_item_preinstall
    old_importFile = _old_portal_type_workflow_chain_template_item_importFile

    # set PortalTypeWorkflowChainTemplateItem to old version
    PortalTypeWorkflowChainTemplateItem.preinstall = old_preinstall
    PortalTypeWorkflowChainTemplateItem._importFile = old_importFile

    # import and install test business template
    repository_path = os.path.join(os.path.dirname(__file__), 'test_data')
    template_path = os.path.join(repository_path,
      'BusinessTemplate_test_compatibility_with_previously_installed_version')

    self.template_tool = self.getTemplateTool()
    import_template = self.template_tool.download(url='file:'+template_path)
    import_template.install(force=1)

    # check that the workflow chain was installed in the portal correctly
    pw = self.getWorkflowTool()
    foo_chain = pw._chains_by_type['Foo']
    self.assertEquals(len(foo_chain), 1)
    self.assertEquals(foo_chain[0], 'edit_workflow')

    # check that modified_object_list is empty (maybe not needed here)
    modified_object_list = import_template.preinstall(check_dependencies = 0)
    self.assertEquals(len(modified_object_list), 0)

    # set PortalTypeWorkflowChainTemplateItem to current version
    PortalTypeWorkflowChainTemplateItem.preinstall = current_preinstall
    PortalTypeWorkflowChainTemplateItem._importFile = current_importFile

    # check that modified_object_list is empty
    modified_object_list = import_template.preinstall(check_dependencies = 0)
    self.assertEquals(len(modified_object_list), 0)
