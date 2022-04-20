##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
assert WITH_LEGACY_WORKFLOW

# State types patch for DCWorkflow
from Products.DCWorkflow.States import StateDefinition
from Products.ERP5Type.Globals import DTMLFile
from Products.ERP5Type import _dtmldir

_properties_form = DTMLFile('state_properties', _dtmldir)

def getAvailableTypeList(self):
  """This is a method specific to ERP5. This returns a list of state types, which are used for portal methods.
  """
  return (
          'draft_order',
          'planned_order',
          'future_inventory',
          'reserved_inventory',
          'transit_inventory',
          'current_inventory',
          )

def setProperties(self, title='', transitions=(), REQUEST=None, description='', type_list=()):
    '''
    '''
    self.title = str(title)
    self.description = str(description)
    self.transitions = tuple(map(str, transitions))
    # This is patched by yo.
    self.type_list = tuple(type_list)
    if REQUEST is not None:
        return self.manage_properties(REQUEST, 'Properties changed.')

def addPossibleTransition(self, tr_ref):
    self.transitions = self.transitions + (tr_ref,)

StateDefinition.addPossibleTransition = addPossibleTransition
StateDefinition._properties_form = _properties_form
StateDefinition.getAvailableTypeList = getAvailableTypeList
StateDefinition.setProperties = setProperties
StateDefinition.type_list = ()
