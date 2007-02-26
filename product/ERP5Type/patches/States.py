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

# State types patch for DCWorkflow
from Products.DCWorkflow.States import StateDefinition
from Globals import DTMLFile
from Products.ERP5Type import _dtmldir

_properties_form = DTMLFile('state_properties', _dtmldir)

def getAvailableTypeList(self):
  """This is a method specific to ERP5. This returns a list of state types, which are used for portal methods.
  """
  return ('current_inventory', 'transit_inventory','reserved_inventory', 
          'future_inventory', 'draft_order', 'planned_order', )
  
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

StateDefinition._properties_form = _properties_form
StateDefinition.getAvailableTypeList = getAvailableTypeList
StateDefinition.setProperties = setProperties
StateDefinition.type_list = ()
