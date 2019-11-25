# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
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
# as published by the Free Software Foundation; either version 2
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

from Products.ERP5Type.ObjectMessage import ObjectMessage
from Products.ERP5Type import Permissions

# Define legacy calls which are superceded by new calls
def getLegacyCallableIdItemList(self):
  return (
      ('WebSection_getPermanentURLForView', 'getPermanentURL'),
    )

# Define acceptable prefix list for skin folder items
skin_prefix_list = None
def getSkinPrefixList(self):
  """
  Return the list of acceptable prefix. Cache the result.

  TODO: make the cache more efficient (read-only transaction
  cache)
  """
  global skin_prefix_list
  if skin_prefix_list:
    return skin_prefix_list

  portal = self.getPortalObject()

  # Add portal types prefix
  portal_types = portal.portal_types
  skin_prefix_list = []
  for portal_type in portal_types.contentValues():
    portal_prefix = portal_type.getId().replace(' ', '')
    skin_prefix_list.append(portal_prefix)

  # Add document classes prefix
  skin_prefix_list.extend(self.portal_types.getDocumentTypeList())

  # Add mixins prefix
  skin_prefix_list.extend(self.portal_types.getMixinTypeList())

  # Add interfaces prefix
  skin_prefix_list.extend(self.portal_types.getInterfaceTypeList())
  # XXX getInterfaceTypeList seems empty ... keep this low-level way for now.
  from Products.ERP5Type import interfaces
  for interface_name in interfaces.__dict__.keys():
    if interface_name.startswith('I'):
      skin_prefix_list.append(interface_name[1:])
      # XXX do we really add with the I prefix ?
      skin_prefix_list.append(interface_name)

  # Add other prefix
  skin_prefix_list.extend((
    'ERP5Type',
    'Module',
    'DCWorkflow', # some workflow script use this, not sure it's correct.
    'Brain', # Catalog brains

    'Entity', # A base class for Person / Organisation
    'Zuite', # Products.Zelenium test suites

    # ERP5Form
    'Form',
    'ListBox',
    'PlanningBox',
    'OOoChart',
  ))

  return set(skin_prefix_list)


# Some skin names that does not respect our conventions but are ignored, for example
# when this naming is used by zope.
ignored_skin_id_set = {
  'twiddleAuthCookie',
  'setAuthCookie',
}

# Generic method to check consistency of a skin item
def checkConsistency(self, fixit=0, source_code=None):
  """
  Make sure skin folder item has appropriate prefix
  and that its source code, if any, does not contain
  calls to legacy methods
  """
  if fixit: raise NotImplementedError
  message_list = []
  portal_path = self.getPortalObject().getPath()
  portal_path_len = len(portal_path)

  # Make sure id is acceptable
  document_id = self.id
  if document_id != document_id.lower() and document_id not in ignored_skin_id_set:
    # Only test prefix with big caps
    prefix = document_id.split('_')[0]
    if prefix not in getSkinPrefixList(self):
      message_list.append(
        ObjectMessage(object_relative_url='/'.join(self.getPhysicalPath())[portal_path_len:],
                      message='Wrong prefix %s for python script %s' % (prefix, document_id)))

  # Make sure source code does not contain legacy callables
  if source_code:
    for legacy_string, new_string in getLegacyCallableIdItemList(self):
      if source_code.find(legacy_string) >= 0:
        message_list.append(
          ObjectMessage(object_relative_url='/'.join(self.getPhysicalPath())[portal_path_len:],
                        message='Source code of %s contains legacy call to %s' % (document_id, legacy_string)))

  return message_list

# Add checkConsistency to Python Scripts
def checkPythonScriptConsistency(self, fixit=0, filter=None, **kw):
  return checkConsistency(self, fixit=fixit, source_code=self.body())

from Products.PythonScripts.PythonScript import PythonScript
PythonScript.checkConsistency= checkPythonScriptConsistency
PythonScript.checkConsistency__roles__ = ('Manager',) # A hack to protect the method

# Add checkConsistency to Page Templates
def checkPageTemplateConsistency(self, fixit=0, filter=None, **kw):
  return checkConsistency(self, fixit=fixit, source_code=self.read())

from Products.PageTemplates.PageTemplate import PageTemplate
PageTemplate.checkConsistency= checkPageTemplateConsistency
PageTemplate.checkConsistency__roles__ = ('Manager',) # A hack to protect the method

